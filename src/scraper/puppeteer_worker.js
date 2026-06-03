/**
 * puppeteer_worker.js - Puppeteer scraper worker.
 *
 * Key fixes:
 * 1. Preflight: detect Chrome error page BEFORE extraction.
 * 2. Disable HTTP/2 (--disable-http2) to reduce ERR_HTTP2_PROTOCOL_ERROR.
 * 3. Use a stable desktop User-Agent for consistent page rendering.
 * 4. opened_real_page=false stops extraction immediately with clear error.
 * 5. No category filtering here. Raw products only. AI Orchestrator filters later.
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const MAX_ATTEMPTS = 2;
const NAV_TIMEOUT_MS = 30000;  // navigation timeout per page
const IDLE_WAIT_MS = 1500;      // wait after load before extracting
const MAX_SCROLL_ROUNDS = Number.parseInt(process.env.MAX_SCROLL_ATTEMPTS || process.env.PUPPETEER_MAX_SCROLL_ROUNDS || argv['max-scrolls'] || '30', 10);
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const STARTED_AT = Date.now();
let currentPhase = 'initializing';

/** Write a JSON line to stdout so Python can parse it. */
function send(payload) {
  try {
    process.stdout.write(JSON.stringify(payload) + '\n');
  } catch (error) {
    process.stderr.write(`[SCRAPER] stdout write failed: ${error.message || error}\n`);
  }
}

function setPhase(phase) {
  currentPhase = phase;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseJsonArray(value, fallback) {
  try {
    const parsed = JSON.parse(value || '[]');
    return Array.isArray(parsed) && parsed.length ? parsed : fallback;
  } catch (_) {
    return fallback;
  }
}

/**
 * Detect if the page is a Chrome network error page.
 * Returns { opened_real_page, error_type } from inside the browser.
 */
async function detectPageHealth(page) {
  const result = await page.evaluate(() => {
    const title = (document.title || '').toLowerCase();
    const body = (document.body ? document.body.innerText || '' : '').toLowerCase().slice(0, 2000);
    const url = location.href.toLowerCase();
    const combined = `${title} ${body} ${url}`;

    // Known Chrome error strings
    const errorPatterns = [
      { pattern: 'captcha',                       key: 'blocked' },
      { pattern: 'verify you are human',          key: 'blocked' },
      { pattern: 'access denied',                 key: 'blocked' },
      { pattern: 'too many requests',             key: 'blocked' },
      { pattern: 'robot',                         key: 'blocked' },
      { pattern: 'err_http2_protocol_error',      key: 'http2_protocol_error' },
      { pattern: 'err_connection_reset',           key: 'connection_reset' },
      { pattern: 'err_connection_refused',         key: 'connection_refused' },
      { pattern: 'err_connection_timed_out',       key: 'connection_timed_out' },
      { pattern: 'err_name_not_resolved',          key: 'name_not_resolved' },
      { pattern: 'err_address_unreachable',        key: 'address_unreachable' },
      { pattern: 'dns_probe_finished_no_internet', key: 'no_internet' },
      { pattern: 'dns_probe_finished_nxdomain',    key: 'dns_nxdomain' },
      { pattern: "this site can",                  key: 'site_unreachable' },
      { pattern: 'situs ini tidak dapat',          key: 'site_unreachable_id' },
    ];

    for (const { pattern, key } of errorPatterns) {
      if (combined.includes(pattern)) {
        return { opened_real_page: false, error_type: key, title, body_sample: body.slice(0, 500) };
      }
    }

    // about:blank or empty means navigation failed silently
    if (url === 'about:blank' || url === '') {
      return { opened_real_page: false, error_type: 'blank_page', title, body_sample: '' };
    }

    // Must have some Tokopedia signal to count as real page
    if (!combined.includes('tokopedia') && !combined.includes('toped')) {
      return {
        opened_real_page: false,
        error_type: 'unknown_non_tokopedia_page',
        title,
        body_sample: body.slice(0, 500),
      };
    }

    return { opened_real_page: true, error_type: null, title, body_sample: body.slice(0, 500) };
  });

  return result;
}

/** Parse Rupiah strings to integers. Python normalizer is final source of truth. */
function parseRupiah(text) {
  if (!text) return null;
  const lower = String(text).toLowerCase().replace(/\s+/g, ' ').trim();
  const unitMatch = lower.match(/(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|rb|ribu|k)\b/i);
  if (unitMatch) {
    const number = Number(unitMatch[1].replace(',', '.'));
    if (!Number.isFinite(number)) return null;
    return Math.round(number * (['juta', 'jt', 'mio'].includes(unitMatch[2].toLowerCase()) ? 1000000 : 1000));
  }
  const parsed = Number.parseInt(lower.replace(/[^\d]/g, ''), 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function cleanUrl(url) {
  return String(url || '').split('?')[0].split('#')[0];
}

/** Build the Tokopedia search URL. No pmin/pmax by default. Budget filter is local. */
function buildSearchUrl(query) {
  return `https://www.tokopedia.com/search?st=product&q=${encodeURIComponent(query)}`;
}

async function configurePage(page, consoleLogs) {
  await page.setViewport({ width: 1366, height: 768, deviceScaleFactor: 1 });
  // Stable desktop UA keeps Tokopedia markup consistent across runs.
  await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  );
  page.setDefaultTimeout(NAV_TIMEOUT_MS);
  page.setDefaultNavigationTimeout(NAV_TIMEOUT_MS);
  page.on('console', (msg) => {
    consoleLogs.push({ type: msg.type(), text: msg.text().slice(0, 500) });
    if (consoleLogs.length > 50) consoleLogs.shift();
  });
}

/** Extract all product cards from the current page DOM. No category filtering. */
async function extractProducts(page, knownKeys, sourceQuery) {
  const rawProducts = await page.evaluate(() => {
    const productCardSelectors = [
      "[data-testid='master-product-card']",
      "div[data-testid*='product']",
      "div.pcv3__container",
      "div[class*='prd_container']",
    ];

    const normalizeLines = (text) =>
      String(text || '')
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);

    const truncateText = (value, maxLen) => {
      const str = String(value || '').replace(/\s+/g, ' ').trim();
      return str.length > maxLen ? str.slice(0, maxLen) + '...' : str;
    };

    const priceFromText = (text) => {
      const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
      return match ? match[0].trim() : '';
    };

    const cleanHref = (href) => String(href || '').split('?')[0].split('#')[0];

    const isProductLikeUrl = (href) => {
      try {
        const url = new URL(href, location.href);
        if (!['www.tokopedia.com', 'tokopedia.com'].includes(url.hostname)) return false;
        const blocked = ['/search', '/cart', '/help', '/discovery', '/official-store'];
        if (blocked.some((prefix) => url.pathname.startsWith(prefix))) return false;
        return url.pathname.split('/').filter(Boolean).length >= 2;
      } catch (_) {
        return false;
      }
    };

    const findContainer = (anchor) => {
      let node = anchor;
      for (let depth = 0; depth < 5 && node; depth += 1) {
        if ((node.innerText || '').includes('Rp')) return node;
        node = node.parentElement;
      }
      return anchor;
    };

    function isBadProductImage(url = '', alt = '', className = '', parentClassName = '', contextText = '') {
      const text = `${url} ${alt} ${className} ${parentClassName} ${contextText}`.toLowerCase();
      const badKeywords = [
        'promo',
        'promo guncang',
        'banner',
        'campaign',
        'ads',
        'iklan',
        'guncang',
        'cashback',
        'voucher',
        'flash',
        'sale',
        'bebas ongkir',
        'bebas-ongkir',
        'free ongkir',
        'free-ongkir',
        'tokopedia.com/promo',
        '/promo/',
        '/campaign/',
        'assets/promo',
        'assets/campaign',
        '6.6',
        '7.7',
        '8.8',
        '9.9',
        '10.10',
        '11.11',
        '12.12',
      ];
      return badKeywords.some((keyword) => text.includes(keyword));
    }

    function normalizeImageUrl(raw) {
      if (typeof raw !== 'string') return '';
      let url = raw.trim();
      if (!url) return '';
      if (url.startsWith('//')) url = `https:${url}`;
      const compact = url.toLowerCase().replace(/\s+/g, '');
      if (['undefined', 'null', 'noimage'].includes(compact)) return '';
      if (compact.includes('svg')) return '';
      if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:image/')) return url;
      return '';
    }

    function scoreProductImageCandidate(img, productTitle = '') {
      const url = normalizeImageUrl(img.src || '');
      const alt = String(img.alt || '');
      const className = String(img.className || '');
      const parentClassName = String(img.parentClassName || '');
      const contextText = String(img.contextText || '');
      if (!url) return -999;
      if (isBadProductImage(url, alt, className, parentClassName, contextText)) return -999;

      let score = 0;
      const width = Number(img.width || 0);
      const height = Number(img.height || 0);
      const ratio = width && height ? width / height : 1;
      if (width >= 180 && height > 0 && ratio > 2.15) return -999;
      if (height >= 180 && width > 0 && ratio < 0.35) return -999;

      if (width >= 120) score += 10;
      if (height >= 120) score += 10;
      if (width >= 250 || height >= 250) score += 8;

      if (ratio >= 0.6 && ratio <= 1.8) score += 10;

      const loweredUrl = url.toLowerCase();
      if (loweredUrl.includes('images.tokopedia.net')) score += 15;
      if (loweredUrl.includes('cache') || loweredUrl.includes('product') || loweredUrl.includes('prd')) score += 8;

      const contextLower = `${className} ${parentClassName} ${contextText}`.toLowerCase();
      if (contextLower.includes('product') || contextLower.includes('prd') || contextLower.includes('master-product-card')) score += 8;
      if (contextLower.includes('image') || contextLower.includes('thumbnail')) score += 4;

      const titleWords = String(productTitle)
        .toLowerCase()
        .split(/\s+/)
        .filter((word) => word.length >= 4)
        .slice(0, 6);
      const altLower = alt.toLowerCase();
      score += titleWords.filter((word) => altLower.includes(word)).length * 8;

      return score;
    }

    function pickBestProductImage(images, productTitle = '') {
      return images
        .map((img) => ({
          src: normalizeImageUrl(img.src || ''),
          score: scoreProductImageCandidate(img, productTitle),
        }))
        .filter((img) => img.src && img.score > 0)
        .sort((a, b) => b.score - a.score)[0]?.src || '';
    }

    function getImageFromCard(card, productTitle = '') {
      const images = [];
      const pushCandidate = (src, node = {}) => {
        const url = normalizeImageUrl(src);
        if (!url) return;
        const rect = typeof node.getBoundingClientRect === 'function' ? node.getBoundingClientRect() : {};
        const parentClasses = [];
        let parent = node.parentElement;
        for (let depth = 0; depth < 4 && parent; depth += 1) {
          parentClasses.push(parent.className || parent.getAttribute?.('class') || '');
          parentClasses.push(parent.getAttribute?.('data-testid') || '');
          parentClasses.push(parent.getAttribute?.('aria-label') || '');
          parent = parent.parentElement;
        }
        images.push({
          src: url,
          alt: node.alt || node.getAttribute?.('alt') || node.getAttribute?.('aria-label') || '',
          className: node.className || node.getAttribute?.('class') || '',
          parentClassName: parentClasses.join(' '),
          contextText: node.getAttribute?.('data-testid') || node.getAttribute?.('aria-label') || '',
          width: node.naturalWidth || node.width || Math.round(rect.width || 0),
          height: node.naturalHeight || node.height || Math.round(rect.height || 0),
        });
      };

      const pushSrcset = (srcset, node) => {
        if (!srcset) return;
        String(srcset)
          .split(',')
          .map((item) => item.trim().split(/\s+/)[0])
          .filter(Boolean)
          .forEach((url) => pushCandidate(url, node));
      };

      const pushBackgroundUrl = (node) => {
        if (!node) return;
        const style = window.getComputedStyle(node);
        const raw = style && style.backgroundImage;
        const match = raw && raw.match(/url\(["']?([^"')]+)["']?\)/i);
        if (match) pushCandidate(match[1], node);
      };

      card.querySelectorAll('picture source, source').forEach((source) => {
        pushSrcset(source.getAttribute('srcset'), source);
        pushSrcset(source.getAttribute('data-srcset'), source);
      });

      card.querySelectorAll('img').forEach((img) => {
        pushCandidate(img.currentSrc, img);
        pushCandidate(img.src, img);
        pushCandidate(img.getAttribute('src'), img);
        pushCandidate(img.getAttribute('data-src'), img);
        pushCandidate(img.getAttribute('data-original-src'), img);
        pushCandidate(img.getAttribute('data-original'), img);
        pushCandidate(img.getAttribute('data-lazy-src'), img);
        pushCandidate(img.getAttribute('data-image'), img);
        pushCandidate(img.getAttribute('data-url'), img);
        pushSrcset(img.getAttribute('srcset'), img);
        pushSrcset(img.getAttribute('data-srcset'), img);
      });

      pushBackgroundUrl(card);
      card.querySelectorAll('[style*="background"]').forEach(pushBackgroundUrl);

      return pickBestProductImage(images, productTitle);
    }

    const productFromContainer = (container, sourceAnchor = null) => {
      const text = container.innerText || sourceAnchor?.innerText || '';
      const priceRaw = priceFromText(text);
      const lines = normalizeLines(text);
      const titleNode =
        container.querySelector?.("[data-testid='spnSRPProdName']") ||
        container.querySelector?.("[data-testid*='ProdName']") ||
        container.querySelector?.('.prd_link-product-name');
      const anchor = sourceAnchor || Array.from(container.querySelectorAll?.("a[href*='tokopedia.com']") || [])
        .find((item) => isProductLikeUrl(item.href));
      const priceIndex = lines.findIndex((line) => priceRaw && line.includes(priceRaw));
      const fallbackTitle =
        (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
        anchor?.getAttribute('title') ||
        lines.find((line) => !line.startsWith('Rp') && line.length > 4) ||
        '';
      const title = (titleNode?.textContent || fallbackTitle || '').trim();
      const imageUrl = getImageFromCard(container, title);
      const url = cleanHref(anchor?.href || '');
      const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
      const sold = (text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i) || [])[0] || '';
      const rating = (text.match(/\b([4-5](?:[.,]\d)?)\b/) || [])[1] || '';

      // Keep product even if shop/rating is empty. Normalizer handles missing fields.
      if (!title || (!url && !priceRaw)) return null;
      return {
        title: truncateText(title, 180),
        price_raw: priceRaw,
        shop: truncateText(afterPrice[0], 80),
        location: truncateText(afterPrice[1], 80),
        rating: truncateText(rating, 10),
        sold: truncateText(sold, 30),
        url: truncateText(url, 500),
        image_url: truncateText(imageUrl || '', 500),
        image: truncateText(imageUrl || '', 500),
        thumbnail: truncateText(imageUrl || '', 500),
        source_engine: 'puppeteer',
      };
    };

    const results = [];
    const seen = new Set();
    const pushProduct = (product) => {
      if (!product) return;
      const key = `${product.url}|${product.title}|${product.price_raw}`;
      if (seen.has(key)) return;
      seen.add(key);
      results.push(product);
    };

    for (const selector of productCardSelectors) {
      document.querySelectorAll(selector).forEach((card) => pushProduct(productFromContainer(card)));
    }

    // Fallback: anchor-based scan for pages with non-standard card markup
    document.querySelectorAll("a[href*='tokopedia.com']").forEach((anchor) => {
      if (!isProductLikeUrl(anchor.href)) return;
      pushProduct(productFromContainer(findContainer(anchor), anchor));
    });

    return results;
  });

  const products = [];
  for (const product of rawProducts) {
    const url = cleanUrl(product.url);
    const key = `${url}|${product.title}|${product.price_raw}`;
    if (knownKeys.has(key)) continue;
    knownKeys.add(key);
    product.url = url;
    product.price_value = parseRupiah(product.price_raw);
    product.source_query = sourceQuery;
    products.push(product);
  }
  return products;
}

/**
 * Save debug file when engine fails or page doesn't open.
 * This is the critical file that explains WHY raw=0 happened.
 */
async function saveEngineErrorDebug({
  searchId, query, urlsTried, preflightResult, errors, page, engineName,
}) {
  const debugDir = path.join(PROJECT_ROOT, 'data', 'debug', searchId);
  const payload = {
    engine: engineName,
    query,
    urls_tried: urlsTried,
    opened_real_page: (preflightResult && preflightResult.opened_real_page) || false,
    error_type: (preflightResult && preflightResult.error_type) || 'unknown',
    page_title: (preflightResult && preflightResult.title) || '',
    body_text_sample: (preflightResult && preflightResult.body_sample) || '',
    selector_counts: {},
    errors,
    recommendation: preflightResult && !preflightResult.opened_real_page
      ? 'Browser opened error page. Not a selector problem. Check network/proxy/HTTP2 support.'
      : 'Page opened but no products extracted. Check selectors or try different query.',
  };

  try {
    fs.mkdirSync(debugDir, { recursive: true });
    if (page && payload.opened_real_page) {
      // Only probe DOM if we actually got a real page
      try {
        payload.selector_counts = await page.evaluate(() => ({
          master_product_card: document.querySelectorAll("[data-testid='master-product-card']").length,
          product_testid: document.querySelectorAll("[data-testid*='product']").length,
          tokopedia_anchors: document.querySelectorAll("a[href*='tokopedia.com']").length,
          img_count: document.querySelectorAll('img').length,
        }));
      } catch (_) {}
      // Save screenshot for debugging
      const ssPath = path.join(debugDir, `${engineName}_engine_error_screenshot.png`);
      await page.screenshot({ path: ssPath, fullPage: true }).catch(() => {});
      payload.screenshot_saved = fs.existsSync(ssPath);
    }
    fs.writeFileSync(
      path.join(debugDir, `${engineName}_engine_error.json`),
      JSON.stringify(payload, null, 2),
      'utf8'
    );
  } catch (err) {
    payload.errors.push(`debug save failed: ${err.message || err}`);
  }

  send({ type: 'debug', data: payload });
  return payload;
}

async function saveImageMissingDebug({ searchId, query, url, products, page, engineName }) {
  const total = products.length;
  if (total < 5) return;
  const missing = products.filter((product) => !product.image).length;
  const missingRate = missing / total;
  if (missingRate <= 0.70) return;

  const debugDir = path.join(PROJECT_ROOT, 'data', 'debug', searchId);
  const payload = {
    engine: engineName,
    query,
    url,
    images_extracted_count: total - missing,
    images_missing_count: missing,
    missing_rate: Number(missingRate.toFixed(4)),
    samples: products.slice(0, 20),
  };

  try {
    fs.mkdirSync(debugDir, { recursive: true });
    const htmlPath = path.join(debugDir, `${engineName}_image_missing_debug.html`);
    const screenshotPath = path.join(debugDir, `${engineName}_image_missing_debug.png`);
    fs.writeFileSync(htmlPath, await page.content(), 'utf8');
    await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
    payload.html_saved = fs.existsSync(htmlPath);
    payload.screenshot_saved = fs.existsSync(screenshotPath);
    fs.writeFileSync(
      path.join(debugDir, `${engineName}_image_missing_debug.json`),
      JSON.stringify(payload, null, 2),
      'utf8'
    );
  } catch (error) {
    payload.error = error && error.message ? error.message : String(error);
  }

  send({ type: 'debug', data: payload });
}

async function scrapeUrl(page, url, query, targetRemaining, knownKeys, searchId) {
  setPhase('opening_page');
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT_MS });
  await page.waitForSelector('body', { timeout: 10000 });
  await sleep(IDLE_WAIT_MS);

  const products = [];
  for (let round = 0; round < MAX_SCROLL_ROUNDS && products.length < targetRemaining; round += 1) {
    setPhase(round === 0 ? 'extracting' : 'scrolling');
    const extracted = await extractProducts(page, knownKeys, query);
    for (const product of extracted) {
      products.push(product);
      send({ type: 'product', data: product });
      if (products.length >= targetRemaining) break;
    }
    await page.evaluate(() => window.scrollBy(0, Math.floor(window.innerHeight * 0.85))).catch(() => {});
    await sleep(700);
  }
  await saveImageMissingDebug({
    searchId,
    query,
    url,
    products,
    page,
    engineName: 'puppeteer',
  });
  return products;
}

async function runAttempt({ query, variants, target, searchId, attempt }) {
  let browser;
  let lastPage = null;
  const products = [];
  const knownKeys = new Set();
  const urlsTried = [];
  const errors = [];
  const consoleLogs = [];

  try {
    setPhase('launching_browser');
    send({
      type: 'progress',
      stage: 'launching_browser',
      percent: 8,
      attempt,
      max_attempts: MAX_ATTEMPTS,
      message: `Opening browser attempt ${attempt}/${MAX_ATTEMPTS}`,
    });

    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-http2',             // reduce ERR_HTTP2_PROTOCOL_ERROR without bypassing access controls
        '--window-size=1366,768',
      ],
    });

    for (let variantIndex = 0; variantIndex < variants.length && products.length < target; variantIndex += 1) {
      const variant = variants[variantIndex];
      // Rule: use simple URL first (no pmin/pmax). Budget filter is local.
      const url = buildSearchUrl(variant);
      urlsTried.push(url);

      const page = await browser.newPage();
      lastPage = page;
      await configurePage(page, consoleLogs);

      setPhase('opening_page');
      send({
        type: 'progress',
        stage: 'opening_page',
        percent: Math.min(55, 10 + variantIndex * 3),
        attempt,
        max_attempts: MAX_ATTEMPTS,
        query: variant,
        message: `Opening variant ${variantIndex + 1}/${variants.length}: ${variant}`,
      });

      try {
        // Navigate and do preflight check before extracting
        setPhase('opening_page');
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT_MS });
        await sleep(800);

        const health = await detectPageHealth(page);

        if (!health.opened_real_page) {
          // STOP. Do not attempt extraction on error page.
          errors.push(`${url}: opened_real_page=false error_type=${health.error_type}`);
          await saveEngineErrorDebug({
            searchId, query, urlsTried,
            preflightResult: { ...health, title: health.title, body_sample: health.body_sample },
            errors, page, engineName: 'puppeteer',
          });

          // Send structured error so Python knows exactly what happened.
          send({
            type: 'preflight_failed',
            opened_real_page: false,
            error_type: health.error_type,
            page_title: health.title,
            body_text_sample: health.body_sample,
            url,
            message: `Browser opened Chrome error page (${health.error_type}), not Tokopedia. Extraction impossible.`,
          });

          await page.close().catch(() => {});
          continue;  // try next variant (different query might work with different DNS cache)
        }

        // Real Tokopedia page confirmed. Extract raw products.
        await page.waitForSelector('body', { timeout: 5000 });
        const before = products.length;
        setPhase('scrolling');
        const extracted = await scrapeUrl(page, url, variant, target - products.length, knownKeys, searchId);
        products.push(...extracted);
        if (products.length === before) {
          errors.push(`zero products for ${url} (page opened OK, selectors found nothing)`);
        }
      } catch (error) {
        errors.push(`${url}: ${error.message || error}`);
      } finally {
        await page.close().catch(() => {});
      }
    }

    if (!products.length) {
      if (lastPage) {
        await saveEngineErrorDebug({
          searchId, query, urlsTried, preflightResult: null,
          errors, page: lastPage, engineName: 'puppeteer',
        });
      }
      throw new Error('Puppeteer extracted zero products from all query variants');
    }

    return products;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

// ── Main entry ─────────────────────────────────────────────────────────────
(async () => {
  const query = argv.query || '';
  const target = Number.parseInt(argv.target || '100', 10);
  const searchId = argv['search-id'] || 'unknown';
  const variants = parseJsonArray(argv.variants, [query]);
  let lastError = '';
  const heartbeat = setInterval(() => {
    send({
      type: 'heartbeat',
      phase: currentPhase,
      elapsed: Number(((Date.now() - STARTED_AT) / 1000).toFixed(1)),
    });
  }, 5000);
  heartbeat.unref?.();

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const products = await runAttempt({ query, variants, target, searchId, attempt });
      setPhase('finalizing');
      clearInterval(heartbeat);
      send({ type: 'result', products });
      process.exit(0);
    } catch (error) {
      lastError = error && error.message ? error.message : String(error);
      send({
        type: 'progress',
        stage: 'puppeteer_retry',
        percent: attempt < MAX_ATTEMPTS ? 58 : 60,
        attempt,
        max_attempts: MAX_ATTEMPTS,
        message: `Puppeteer attempt ${attempt} failed: ${lastError}`,
      });
      await sleep(1000);
    }
  }

  clearInterval(heartbeat);
  send({ type: 'error', message: lastError || 'Unknown Puppeteer error' });
  process.exit(1);
})().catch((error) => {
  send({
    type: 'error',
    message: error && error.message ? error.message : String(error),
    stack: error && error.stack ? error.stack : '',
  });
  process.exit(1);
});
