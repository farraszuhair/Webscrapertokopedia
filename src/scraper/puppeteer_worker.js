const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const MAX_ATTEMPTS = 2;
const PER_QUERY_TIMEOUT_MS = 22000;

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
  // Python parser remains final truth. JS parser is for useful streamed data.
  if (!text) return null;
  const lower = String(text).toLowerCase().replace(/\s+/g, ' ').trim();
  if (!lower || lower.includes('hubungi penjual')) return null;

  const unitMatch = lower.match(/(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|rb|ribu|k)\b/i);
  if (unitMatch) {
    const number = Number(unitMatch[1].replace(',', '.'));
    if (!Number.isFinite(number)) return null;
    const unit = unitMatch[2].toLowerCase();
    return Math.round(number * (['juta', 'jt', 'mio'].includes(unit) ? 1000000 : 1000));
  }

  const digits = lower.replace(/[^\d]/g, '');
  const parsed = Number.parseInt(digits, 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function cleanUrl(url) {
  return String(url || '').split('?')[0].split('#')[0];
}

function buildSearchUrl(query, minPrice, maxPrice) {
  const params = new URLSearchParams();
  params.set('st', 'product');
  params.set('q', query);
  params.set('sort', '5');
  if (minPrice) params.set('pmin', String(minPrice));
  if (maxPrice) params.set('pmax', String(maxPrice));
  return `https://www.tokopedia.com/search?${params.toString()}`;
}

async function configurePage(page) {
  // Reliability only: stable viewport and finite browser timeouts.
  await page.setViewport({ width: 1366, height: 768, deviceScaleFactor: 1 });
  page.setDefaultTimeout(PER_QUERY_TIMEOUT_MS);
  page.setDefaultNavigationTimeout(PER_QUERY_TIMEOUT_MS);
}

async function extractProducts(page, knownUrls, sourceQuery) {
  const rawProducts = await page.evaluate(() => {
    const parsePrice = (text) => {
      const match = String(text || '').match(/Rp\s*[\d.,]+(?:\s*(?:juta|jt|mio|rb|ribu|k))?/i);
      return match ? match[0].trim() : '';
    };

    const isProductUrl = (href) => {
      const url = String(href || '');
      if (!url.includes('tokopedia.com/')) return false;
      if (url.includes('/search') || url.includes('/cart') || url.includes('/help')) return false;
      if (url.includes('/p/') || url.includes('/official-store')) return false;
      return true;
    };

    const textLines = (text) =>
      String(text || '')
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);

    const findTitle = (card, anchor, lines, priceRaw) => {
      const titleNode =
        card.querySelector('[data-testid="spnSRPProdName"]') ||
        card.querySelector('.prd_link-product-name');
      if (titleNode && titleNode.textContent.trim()) return titleNode.textContent.trim();

      const priceIndex = lines.findIndex((line) => line.includes(priceRaw));
      if (priceIndex > 0) return lines[priceIndex - 1];

      const candidate = lines.find(
        (line) =>
          !line.startsWith('Rp') &&
          !/terjual|rating|official|kota|kab\./i.test(line) &&
          line.length > 4
      );
      return candidate || (anchor.getAttribute('title') || '').trim() || 'Produk Tokopedia';
    };

    const findImage = (card) => {
      const img = card.querySelector('img');
      if (!img) return '';
      return img.currentSrc || img.src || img.getAttribute('data-src') || '';
    };

    const anchors = Array.from(document.querySelectorAll('a[href*="tokopedia.com/"]'));
    const results = [];

    for (const anchor of anchors) {
      const href = anchor.href || '';
      if (!isProductUrl(href)) continue;

      const card =
        anchor.closest('[data-testid="master-product-card"]') ||
        anchor.closest('div.pcv3__container') ||
        anchor.closest('div[class*="css-"]') ||
        anchor;
      const text = card.innerText || anchor.innerText || '';
      const priceRaw = parsePrice(text);
      if (!priceRaw) continue;

      const lines = textLines(text);
      const title = findTitle(card, anchor, lines, priceRaw);
      const priceIndex = lines.findIndex((line) => line.includes(priceRaw));
      const afterPrice = priceIndex >= 0 ? lines.slice(priceIndex + 1) : lines;
      const sold = (text.match(/(\d+(?:[.,]\d+)?\s*(?:rb|jt)?\+?)\s*(?:terjual|sold)/i) || [])[0] || '';
      const rating = (text.match(/\b([4-5](?:[.,]\d)?)\b/) || [])[1] || '';

      results.push({
        title,
        price_raw: priceRaw,
        shop: afterPrice[0] || '',
        location: afterPrice[1] || '',
        rating,
        sold,
        url: href.split('?')[0],
        image: findImage(card),
        source_engine: 'puppeteer',
      });
    }

    return results;
  });

  const products = [];
  for (const product of rawProducts) {
    const url = cleanUrl(product.url);
    if (!url || knownUrls.has(url)) continue;
    knownUrls.add(url);
    product.url = url;
    product.price_value = parseRupiah(product.price_raw);
    product.source_query = sourceQuery;
    products.push(product);
  }
  return products;
}

async function scrapeQuery(browser, query, target, knownUrls, minPrice, maxPrice, attempt, index, total) {
  const page = await browser.newPage();
  try {
    await configurePage(page);
    const url = buildSearchUrl(query, minPrice, maxPrice);
    send({
      type: 'progress',
      stage: 'puppeteer_query',
      percent: Math.min(42, 10 + index * 3),
      attempt,
      max_attempts: MAX_ATTEMPTS,
      query,
      message: `Scraping ${query} (${index + 1}/${total}) with price params ${minPrice || '-'}-${maxPrice || '-'}`,
    });

    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PER_QUERY_TIMEOUT_MS });
    await page.waitForSelector('body', { timeout: 8000 });

    const products = [];
    for (let round = 0; round < 7 && products.length < target; round += 1) {
      await page.evaluate(() => window.scrollBy(0, Math.floor(window.innerHeight * 0.9)));
      await sleep(500);

      const extracted = await extractProducts(page, knownUrls, query);
      for (const product of extracted) {
        products.push(product);
        send({ type: 'product', data: product });
        if (products.length >= target) break;
      }
    }

    return products;
  } finally {
    await page.close().catch(() => {});
  }
}

async function runAttempt(variants, target, minPrice, maxPrice, attempt) {
  let browser;
  const products = [];
  const knownUrls = new Set();

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

    for (let index = 0; index < variants.length && products.length < target; index += 1) {
      const query = variants[index];
      try {
        const extracted = await scrapeQuery(
          browser,
          query,
          target - products.length,
          knownUrls,
          minPrice,
          maxPrice,
          attempt,
          index,
          variants.length
        );
        products.push(...extracted);
      } catch (error) {
        send({
          type: 'progress',
          stage: 'puppeteer_query_failed',
          percent: Math.min(44, 10 + index * 3),
          attempt,
          max_attempts: MAX_ATTEMPTS,
          query,
          message: `Query failed: ${query} - ${error.message || error}`,
        });
      }
    }

    if (!products.length) throw new Error('Puppeteer extracted zero products from all query variants');
    send({
      type: 'progress',
      stage: 'puppeteer_extracting',
      percent: 45,
      attempt,
      max_attempts: MAX_ATTEMPTS,
      message: `Puppeteer extracted ${products.length} products from ${variants.length} variants`,
    });
    return products;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

(async () => {
  const query = argv.query || '';
  const target = Number.parseInt(argv.target || '100', 10);
  const variants = parseJsonArray(argv.variants, [query]);
  const minPrice = argv['min-price'] ? Number.parseInt(argv['min-price'], 10) : null;
  const maxPrice = argv['max-price'] ? Number.parseInt(argv['max-price'], 10) : null;
  let lastError = '';

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const products = await runAttempt(variants, target, minPrice, maxPrice, attempt);
      send({ type: 'done', products });
      process.exit(0);
    } catch (error) {
      lastError = error && error.message ? error.message : String(error);
      send({
        type: 'progress',
        stage: 'puppeteer_retry',
        percent: attempt < MAX_ATTEMPTS ? 46 : 47,
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
