const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const MAX_ATTEMPTS = 2;
const PER_QUERY_TIMEOUT_MS = 25000;
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');

function send(payload) {
  process.stdout.write(JSON.stringify(payload) + '\n');
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

function parseRupiah(text) {
  // Python parser is final. JS parser keeps streamed raw products useful.
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

function buildSearchUrl(query, minPrice, maxPrice, usePriceParams) {
  const params = [`st=product`, `q=${encodeURIComponent(query)}`];
  if (usePriceParams && minPrice) params.push(`pmin=${encodeURIComponent(String(minPrice))}`);
  if (usePriceParams && maxPrice) params.push(`pmax=${encodeURIComponent(String(maxPrice))}`);
  return `https://www.tokopedia.com/search?${params.join('&')}`;
}

function urlsForVariant(query, minPrice, maxPrice) {
  const urls = [buildSearchUrl(query, minPrice, maxPrice, false)];
  if (minPrice || maxPrice) urls.push(buildSearchUrl(query, minPrice, maxPrice, true));
  return urls;
}

async function configurePage(page, consoleLogs) {
  // Reliability only: stable viewport and finite timeouts.
  await page.setViewport({ width: 1366, height: 768, deviceScaleFactor: 1 });
  page.setDefaultTimeout(PER_QUERY_TIMEOUT_MS);
  page.setDefaultNavigationTimeout(PER_QUERY_TIMEOUT_MS);
  page.on('console', (msg) => {
    consoleLogs.push({ type: msg.type(), text: msg.text().slice(0, 500) });
    if (consoleLogs.length > 50) consoleLogs.shift();
  });
}

async function probePage(page) {
  return page.evaluate(() => {
    const count = (selector) => document.querySelectorAll(selector).length;
    const bodyText = document.body ? document.body.innerText || '' : '';
    return {
      "[data-testid='master-product-card']": count("[data-testid='master-product-card']"),
      "[data-testid*='product']": count("[data-testid*='product']"),
      "a[href*='tokopedia.com']": count("a[href*='tokopedia.com']"),
      img: count('img'),
      body_text_length: bodyText.length,
      body_text_sample: bodyText.slice(0, 1000),
    };
  });
}

async function saveZeroRawDebug({ searchId, query, variants, urlsTried, pagesLoaded, probes, consoleLogs, errors, page }) {
  const debugDir = path.join(PROJECT_ROOT, 'data', 'debug', searchId);
  const payload = {
    engine: 'puppeteer',
    query,
    query_variants: variants,
    urls_tried: urlsTried,
    pages_loaded: pagesLoaded,
    selector_results: probes[probes.length - 1] || {},
    html_saved: false,
    screenshot_saved: false,
    console_logs: consoleLogs,
    current_url: '',
    page_title: '',
    body_text_sample: '',
    errors,
  };

  try {
    fs.mkdirSync(debugDir, { recursive: true });
    if (page) {
      payload.current_url = page.url();
      payload.page_title = await page.title().catch(() => '');
      const html = await page.content().catch(() => '');
      const bodyText = await page.evaluate(() => (document.body ? document.body.innerText || '' : '')).catch(() => '');
      payload.body_text_sample = bodyText.slice(0, 1000);
      fs.writeFileSync(path.join(debugDir, 'puppeteer_zero_raw_page.html'), html, 'utf8');
      payload.html_saved = Boolean(html);
      await page.screenshot({ path: path.join(debugDir, 'puppeteer_zero_raw_screenshot.png'), fullPage: true }).catch(() => {});
      payload.screenshot_saved = fs.existsSync(path.join(debugDir, 'puppeteer_zero_raw_screenshot.png'));
    }
    fs.writeFileSync(path.join(debugDir, 'puppeteer_zero_raw_debug.json'), JSON.stringify(payload, null, 2), 'utf8');
  } catch (error) {
    payload.errors.push(`debug save failed: ${error.message || error}`);
  }

  send({ type: 'debug', data: payload });
}

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

    const priceFromText = (text) => {
      const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
      return match ? match[0].trim() : '';
    };

    const cleanHref = (href) => String(href || '').split('?')[0].split('#')[0];

    const isProductLikeUrl = (href) => {
      try {
        const url = new URL(href, location.href);
        if (!url.hostname.includes('tokopedia.com')) return false;
        const blocked = ['/search', '/cart', '/help', '/discovery', '/official-store'];
        if (blocked.some((prefix) => url.pathname.startsWith(prefix))) return false;
        const segments = url.pathname.split('/').filter(Boolean);
        return segments.length >= 2;
      } catch (_) {
        return false;
      }
    };

    const findContainer = (anchor) => {
      let node = anchor;
      for (let depth = 0; depth < 5 && node; depth += 1) {
        const text = node.innerText || '';
        if (text.includes('Rp')) return node;
        node = node.parentElement;
      }
      return anchor;
    };

    const productFromContainer = (container, sourceAnchor = null) => {
      const text = container.innerText || sourceAnchor?.innerText || '';
      const priceRaw = priceFromText(text);
      const lines = normalizeLines(text);
      const titleNode =
        container.querySelector?.("[data-testid='spnSRPProdName']") ||
        container.querySelector?.("[data-testid*='ProdName']") ||
        container.querySelector?.(".prd_link-product-name");
      const anchor = sourceAnchor || container.querySelector?.("a[href*='tokopedia.com']");
      const imageNode = container.querySelector?.('img');
      const priceIndex = lines.findIndex((line) => priceRaw && line.includes(priceRaw));
      const fallbackTitle =
        (priceIndex > 0 ? lines[priceIndex - 1] : '') ||
        anchor?.getAttribute('title') ||
        imageNode?.getAttribute('alt') ||
        lines.find((line) => !line.startsWith('Rp') && line.length > 4) ||
        '';
      const title = (titleNode?.textContent || fallbackTitle || '').trim();
      const url = cleanHref(anchor?.href || '');
      const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
      const sold = (text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i) || [])[0] || '';
      const rating = (text.match(/\b([4-5](?:[.,]\d)?)\b/) || [])[1] || '';

      if (!title || (!url && !priceRaw)) return null;
      return {
        title,
        price_raw: priceRaw,
        shop: afterPrice[0] || '',
        location: afterPrice[1] || '',
        rating,
        sold,
        url,
        image: imageNode ? imageNode.currentSrc || imageNode.src || imageNode.getAttribute('data-src') || '' : '',
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

async function scrapeUrl(page, url, query, targetRemaining, knownKeys) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PER_QUERY_TIMEOUT_MS });
  await page.waitForSelector('body', { timeout: 10000 });
  await sleep(1200);

  const products = [];
  for (let round = 0; round < 8 && products.length < targetRemaining; round += 1) {
    const extracted = await extractProducts(page, knownKeys, query);
    for (const product of extracted) {
      products.push(product);
      send({ type: 'product', data: product });
      if (products.length >= targetRemaining) break;
    }
    await page.evaluate(() => window.scrollBy(0, Math.floor(window.innerHeight * 0.85))).catch(() => {});
    await sleep(650);
  }
  return products;
}

async function runAttempt({ query, variants, target, minPrice, maxPrice, searchId, attempt }) {
  let browser;
  let lastPage = null;
  const products = [];
  const knownKeys = new Set();
  const urlsTried = [];
  const probes = [];
  const errors = [];
  const consoleLogs = [];
  let pagesLoaded = 0;

  try {
    send({
      type: 'progress',
      stage: 'puppeteer_opening',
      percent: 8,
      attempt,
      max_attempts: MAX_ATTEMPTS,
      message: `Opening browser attempt ${attempt}/${MAX_ATTEMPTS}`,
    });

    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });

    for (let variantIndex = 0; variantIndex < variants.length && products.length < target; variantIndex += 1) {
      const variant = variants[variantIndex];
      const urls = urlsForVariant(variant, minPrice, maxPrice);

      for (const url of urls) {
        if (products.length >= target) break;
        urlsTried.push(url);
        const page = await browser.newPage();
        lastPage = page;
        await configurePage(page, consoleLogs);

        send({
          type: 'progress',
          stage: 'puppeteer_query',
          percent: Math.min(55, 10 + variantIndex * 3),
          attempt,
          max_attempts: MAX_ATTEMPTS,
          query: variant,
          message: `Opening query variant ${variantIndex + 1}/${variants.length}: ${variant}`,
        });

        try {
          const before = products.length;
          const extracted = await scrapeUrl(page, url, variant, target - products.length, knownKeys);
          products.push(...extracted);
          pagesLoaded += 1;
          probes.push(await probePage(page).catch(() => ({})));
          if (products.length === before) errors.push(`zero products for ${url}`);
        } catch (error) {
          errors.push(`${url}: ${error.message || error}`);
        } finally {
          if (products.length > 0) {
            await page.close().catch(() => {});
          }
        }
      }
    }

    if (!products.length) {
      await saveZeroRawDebug({ searchId, query, variants, urlsTried, pagesLoaded, probes, consoleLogs, errors, page: lastPage });
      throw new Error('Puppeteer extracted zero products from all query variants');
    }

    return products;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

(async () => {
  const query = argv.query || '';
  const target = Number.parseInt(argv.target || '100', 10);
  const searchId = argv['search-id'] || 'unknown';
  const variants = parseJsonArray(argv.variants, [query]);
  const minPrice = argv['min-price'] ? Number.parseInt(argv['min-price'], 10) : null;
  const maxPrice = argv['max-price'] ? Number.parseInt(argv['max-price'], 10) : null;
  let lastError = '';

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const products = await runAttempt({ query, variants, target, minPrice, maxPrice, searchId, attempt });
      send({ type: 'done', products });
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
      await sleep(800);
    }
  }

  send({ type: 'error', error: lastError || 'Unknown Puppeteer error' });
  process.exit(1);
})().catch((error) => {
  send({ type: 'error', error: error && error.message ? error.message : String(error) });
  process.exit(1);
});
