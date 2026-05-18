const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const MAX_ATTEMPTS = 2;
const USER_AGENT =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

function send(payload) {
  process.stdout.write(JSON.stringify(payload) + '\n');
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseRupiah(text) {
  // JS-side parser is only for streaming visibility. Python parser is final truth.
  if (!text) return null;
  const lower = String(text).toLowerCase().replace(/\s+/g, ' ').trim();
  if (!lower || lower.includes('hubungi penjual')) return null;

  const unitMatch = lower.match(/(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|rb|ribu|k)\b/i);
  if (unitMatch) {
    const number = Number(unitMatch[1].replace(',', '.'));
    if (!Number.isFinite(number)) return null;
    const unit = unitMatch[2].toLowerCase();
    const multiplier = ['juta', 'jt', 'mio'].includes(unit) ? 1000000 : 1000;
    return Math.round(number * multiplier);
  }

  const digits = lower.replace(/[^\d]/g, '');
  if (!digits) return null;
  const parsed = Number.parseInt(digits, 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function isRetriableError(error) {
  const message = String(error && error.message ? error.message : error).toLowerCase();
  return [
    'err_http2_protocol_error',
    'err_connection_reset',
    'timeout',
    'detached frame',
    'target closed',
    'session closed',
    'execution context was destroyed',
    'navigation failed',
    'net::',
  ].some((needle) => message.includes(needle));
}

function cleanUrl(url) {
  return String(url || '').split('?')[0].split('#')[0];
}

async function configurePage(page) {
  await page.setViewport({ width: 1366, height: 768, deviceScaleFactor: 1 });
  await page.setUserAgent(USER_AGENT);
  await page.setExtraHTTPHeaders({
    'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
  });

  await page.evaluateOnNewDocument(() => {
    // Hide the strongest automation tell without adding a heavy stealth plugin.
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US', 'en'] });
  });

  await page.setRequestInterception(true);
  page.on('request', (request) => {
    const type = request.resourceType();
    if (['font', 'media'].includes(type)) {
      request.abort();
      return;
    }
    request.continue();
  });
}

async function extractProducts(page, knownUrls) {
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
      const selectorTitle =
        card.querySelector('[data-testid="spnSRPProdName"]') ||
        card.querySelector('.prd_link-product-name');
      if (selectorTitle && selectorTitle.textContent.trim()) {
        return selectorTitle.textContent.trim();
      }

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

  const newProducts = [];
  for (const product of rawProducts) {
    const url = cleanUrl(product.url);
    if (!url || knownUrls.has(url)) continue;
    knownUrls.add(url);
    product.url = url;
    product.price_value = parseRupiah(product.price_raw);
    newProducts.push(product);
  }
  return newProducts;
}

async function runAttempt(query, target, attempt) {
  let browser;
  const products = [];
  const knownUrls = new Set();

  try {
    send({
      type: 'progress',
      stage: 'puppeteer_opening',
      percent: 12,
      attempt,
      max_attempts: MAX_ATTEMPTS,
      message: `Opening Tokopedia attempt ${attempt}/${MAX_ATTEMPTS}`,
    });

    browser = await puppeteer.launch({
      headless: 'new',
      defaultViewport: null,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-quic',
        '--ignore-certificate-errors',
        '--window-size=1366,768',
      ],
    });

    const page = await browser.newPage();
    await configurePage(page);

    const url = `https://www.tokopedia.com/search?navsource=search&q=${encodeURIComponent(query)}`;
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 });
    await page.waitForSelector('body', { timeout: 10000 });

    for (let round = 0; round < 14 && products.length < target; round += 1) {
      send({
        type: 'progress',
        stage: 'puppeteer_scrolling',
        percent: Math.min(38, 16 + round * 2),
        attempt,
        max_attempts: MAX_ATTEMPTS,
        message: `Scrolling Tokopedia, found ${products.length}`,
      });

      await page.evaluate(() => window.scrollBy(0, Math.floor(window.innerHeight * 0.85)));
      await sleep(650 + Math.floor(Math.random() * 300));

      const extracted = await extractProducts(page, knownUrls);
      for (const product of extracted) {
        products.push(product);
        send({ type: 'product', data: product });
        if (products.length >= target) break;
      }

      const bodyText = await page.evaluate(() => document.body.innerText || '');
      if (/captcha|verify|robot/i.test(bodyText)) {
        throw new Error('Tokopedia captcha/robot verification detected');
      }
    }

    send({
      type: 'progress',
      stage: 'puppeteer_extracting',
      percent: 42,
      attempt,
      max_attempts: MAX_ATTEMPTS,
      message: `Puppeteer extracted ${products.length} products`,
    });

    if (!products.length) {
      throw new Error('Puppeteer extracted zero products');
    }

    return products;
  } finally {
    if (browser) {
      await browser.close().catch(() => {});
    }
  }
}

(async () => {
  const query = argv.query || '';
  const target = Number.parseInt(argv.target || '100', 10);
  let lastError = '';

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const products = await runAttempt(query, target, attempt);
      send({ type: 'done', products });
      process.exit(0);
    } catch (error) {
      lastError = error && error.message ? error.message : String(error);
      send({
        type: 'progress',
        stage: 'puppeteer_retry',
        percent: attempt < MAX_ATTEMPTS ? 44 : 45,
        attempt,
        max_attempts: MAX_ATTEMPTS,
        message: `Puppeteer attempt ${attempt} failed: ${lastError}`,
      });

      if (!isRetriableError(error) && attempt >= MAX_ATTEMPTS) break;
      await sleep(900);
    }
  }

  send({ type: 'error', error: lastError || 'Unknown Puppeteer error' });
  process.exit(1);
})().catch((error) => {
  send({ type: 'error', error: error && error.message ? error.message : String(error) });
  process.exit(1);
});
