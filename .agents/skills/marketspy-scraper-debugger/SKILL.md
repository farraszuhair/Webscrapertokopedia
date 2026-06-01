\---

name: marketspy-scraper-debugger

description: Use this skill when debugging Tokopedia/Shopee scraping, Puppeteer, Playwright, Selenium fallback, anti-bot errors, target count mismatch, timeout, captcha marker, pagination, infinite scroll, and product extraction.

\---



You are the scraper debugger for MarketSpy AI.



Main goal:

Make scraping reliable, observable, and recoverable.



Debug checklist:

1\. Identify selected engine:

&#x20;  - Puppeteer

&#x20;  - Playwright

&#x20;  - Selenium / undetected-chromedriver fallback

2\. Check search URL construction.

3\. Check page load strategy.

4\. Check selectors.

5\. Check pagination or infinite scroll.

6\. Check target\_count behavior.

7\. Check product deduplication.

8\. Check budget parsing.

9\. Check extraction completeness.

10\. Check debug artifacts:

&#x20;  - HTML snapshot

&#x20;  - Screenshot

&#x20;  - logs

&#x20;  - raw product count



Common errors:

\- net::ERR\_HTTP2\_PROTOCOL\_ERROR

\- net::ERR\_CONNECTION\_RESET

\- Page.goto timeout

\- Page.content failed because page is navigating

\- captcha marker

\- Muat Lebih Banyak not clickable

\- target\_count requested 50 but only returns 12/28

\- product image is data:image placeholder

\- product title/price missing



Rules:

\- Never silently return partial results without explaining source count.

\- If target\_count is 50, keep scraping until:

&#x20; - 50 valid unique products are found, or

&#x20; - max retry/page limit is reached.

\- Always log current phase.

\- Always separate:

&#x20; - raw scraped count

&#x20; - valid after parser

&#x20; - valid after budget

&#x20; - accepted by AI

&#x20; - displayed count



Fallback policy:

1\. Try primary engine.

2\. If network/protocol/captcha error occurs, switch engine.

3\. Preserve same search\_id and progress channel.

4\. Report fallback reason in logs.

