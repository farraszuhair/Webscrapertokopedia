const puppeteer = require('puppeteer');
const argv = require('minimist')(process.argv.slice(2));

const send = (msg) => console.log(JSON.stringify(msg));

(async () => {
    const query = argv.query || '';
    const target = argv.target || 100;
    
    send({type: "progress", stage: "puppeteer_starting", percent: 8, message: "Membuka browser (Puppeteer)..."});
    
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: "new",
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        });
        const page = await browser.newPage();
        
        await page.setViewport({ width: 1280, height: 800 });
        
        const url = `https://www.tokopedia.com/search?navsource=search&q=${encodeURIComponent(query)}`;
        send({type: "progress", stage: "puppeteer_opening", percent: 12, message: "Membuka Tokopedia..."});
        
        // Timeout 15000ms as requested
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
        
        send({type: "progress", stage: "puppeteer_scrolling", percent: 20, message: "Scroll halaman..."});
        
        // basic scroll & extract loop for puppeteer, if it fails early it will throw, which is what we want for fallback
        let products = [];
        let previousHeight = 0;
        
        for (let i=0; i<10; i++) {
            await page.evaluate(() => window.scrollBy(0, 800));
            await new Promise(r => setTimeout(r, 1000));
            
            const currentHeight = await page.evaluate(() => document.body.scrollHeight);
            if (currentHeight === previousHeight) break;
            previousHeight = currentHeight;
            
            // extract cards
            const extracted = await page.evaluate(() => {
                const results = [];
                document.querySelectorAll('a[href*="tokopedia.com"]').forEach(a => {
                    if (a.innerText && a.innerText.includes('Rp')) {
                        const url = a.href.split('?')[0];
                        const text = a.innerText;
                        const matchPrice = text.match(/Rp\s*[0-9.,]+/);
                        if (matchPrice && !url.includes('/p/')) {
                            results.push({
                                url: url,
                                title: a.innerText.split('\n')[0] || 'Produk',
                                price_text: matchPrice[0]
                            });
                        }
                    }
                });
                return results;
            });
            
            for (let item of extracted) {
                if (!products.some(p => p.url === item.url)) {
                    products.push(item);
                }
            }
            
            if (products.length >= target) break;
        }
        
        send({type: "progress", stage: "puppeteer_extracting", percent: 35, message: `Ekstrak ${products.length} produk...`});
        
        send({type: "done", products: products});
        
    } catch(err) {
        send({type: "error", error: err.message});
        process.exit(0); // Exit 0 so python reads the error json cleanly
    } finally {
        if (browser) await browser.close();
    }
})();
