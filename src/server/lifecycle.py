import asyncio
from typing import Dict
from src.utils.logger import log

_scrape_tasks: Dict[str, asyncio.Task] = {}

def register_task(search_id: str, task: asyncio.Task):
    _scrape_tasks[search_id] = task

def unregister_task(search_id: str):
    _scrape_tasks.pop(search_id, None)

def get_scrape_task(search_id: str) -> asyncio.Task:
    return _scrape_tasks.get(search_id)

async def cancel_all_tasks():
    if _scrape_tasks:
        log("LIFECYCLE", f"Cancelling {len(_scrape_tasks)} background scrape tasks...", "WARN")
        for search_id, task in _scrape_tasks.items():
            task.cancel()
        
        # Wait for cancellation to complete
        await asyncio.gather(*_scrape_tasks.values(), return_exceptions=True)
        _scrape_tasks.clear()
        log("LIFECYCLE", "All background tasks cancelled. Browser resources cleaned up.", "OK")
