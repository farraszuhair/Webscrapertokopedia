# Changelog

All notable changes to MarketSpy AI are documented in this file.

## [1.1.0] - 2026-04-20

### Fixed
- **CRITICAL: Mousepad Search Returns 0 Products** 
  - Root cause: Negative keywords filter included 'mousepad' and 'pad', blocking actual mousepad products when searching for "mousepad"
  - Solution: Removed search term keywords from negative_keywords blocklist
  - Impact: Mousepad and other directly-searched items now properly appear in results
  
- **Retry Mechanism Not Working**
  - Added `MAX_RETRIES = 3` and `RETRY_DELAY = 2` configuration
  - Implements exponential retry on failure
  - Proper error logging for each attempt
  
- **Poor Error Messages**
  - Error: "Gagal scrape atau data kosong. Browser mungkin terkena Captcha."
  - Now: Contextual error messages distinguish between Captcha, network, and empty result scenarios
  - HTTP status codes: 503 for service issues, 404 for no results, 400 for bad requests

- **Timeout Exception Not Caught**
  - Added explicit import: `from playwright.async_api import TimeoutError as PlaywrightTimeoutError`
  - Now properly catches and logs Playwright timeout errors

### Added
- **Comprehensive Unit Tests** (9 test cases)
  - Keyword filtering validation
  - Price validation logic
  - Accessory exclusion tests
  - Retry mechanism verification
  - Error handling tests
  
- **Production-Quality Documentation**
  - README.md: User guide with troubleshooting
  - DEVELOPMENT.md: Developer guide with architecture
  - .env.example: Configuration template
  
- **Improved Logging**
  - Consistent logging format using Python logging module
  - Better error context and debugging information
  - Per-attempt retry logging

- **Test Dependencies**
  - Added pytest==7.4.0
  - Added pytest-asyncio==0.21.1

### Changed
- **Refactored Scraper Architecture**
  - Split single search() into search() + _do_search() for better retry handling
  - Moved cleanup logic into finally block
  - Better separation of concerns

- **Improved Keyword Matching**
  - Search terms now dynamically extracted from keyword
  - Negative keywords filtered based on search context
  - More flexible accessory detection

- **Enhanced Price Validation**
  - Added 'headphones' to premium product list
  - Clear minimum price thresholds documented
  - Context-aware price checking

### Improved
- Code maintainability with docstrings
- Async error handling robustness
- Browser resource cleanup reliability
- User feedback clarity

## [1.0.0] - 2026-04-19

### Initial Release
- Tokopedia product scraper with Playwright
- Ollama LLM integration for product analysis
- Flask REST API
- Dashboard web interface
- Product filtering and deduplication
- AI trust score and value score calculation
