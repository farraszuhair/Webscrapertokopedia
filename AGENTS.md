# MarketSpy AI Coding Rules

## Project identity

This project is MarketSpy AI, a marketplace scraping dashboard focused on Tokopedia first, with future marketplace fallback support.

## User preference

- Explain briefly.
- Prefer implementation over theory.
- Give full working code when editing.
- Avoid fake placeholders unless explicitly marked.
- Preserve existing API contracts.
- Use Indonesian comments when helpful for learning.

## Stack assumptions

Backend:
- Python
- FastAPI
- Uvicorn
- WebSocket progress
- Ollama local LLM

Scraping:
- Puppeteer or Playwright primary
- Selenium / undetected-chromedriver fallback when configured

Frontend:
- React / HTML / Tailwind depending on current project structure
- Midnight blue UI direction
- AnimeJS-inspired interaction direction

## Must preserve

- Search flow
- Progress flow
- Result flow
- Feedback flow
- Existing endpoints unless migration is clearly planned

## Before editing

1. Inspect project tree.
2. Identify entry points.
3. Identify frontend framework.
4. Identify backend routes.
5. Identify run commands.
6. Explain changed files after editing.

## Testing

After code changes, run the most relevant command if available:
- npm run build
- npm run lint
- npm test
- python -m pytest
- uvicorn import check

## Safety

- Never commit secrets.
- Never hardcode API keys.
- Never commit local databases, logs, screenshots, or debug dumps.
- Never delete data files without backup.