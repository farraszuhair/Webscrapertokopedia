"""
routes.py - FastAPI routes for the scraping API.
"""
import uuid
import asyncio
import traceback
from typing import Dict, Any, List
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from src.server.schemas import SearchRequest, FeedbackRequest, ProgressResponse
from src.server.progress import init_progress, get_progress, update_progress, complete_progress, fail_progress
from src.utils.logger import log
from src.utils.currency import calculate_budget_range, parse_rupiah
from src.utils.eta import ETACalculator
from src.scraper.engine_selector import run_scraper_chain
from src.ai.relevance import filter_relevance
from src.ai.learning import save_feedback
from src.ai.reset import reset_ai_memory
from src.server.lifecycle import register_task, unregister_task
from src.utils.debug import safe_save_debug

router = APIRouter()

_results_store: Dict[str, Dict[str, Any]] = {}

def cleanup_task(search_id: str, task: asyncio.Task):
    """Callback triggered when task finishes (success, fail, or cancelled)."""
    try:
        exc = task.exception()
        if exc:
            log(f"[{search_id}]", f"Task exception was not handled properly: {exc}", "ERROR")
            # Avoid overwriting a potentially handled failure if it's already recorded,
            # but safe_save_debug is useful here to capture raw leaks.
    except asyncio.CancelledError:
        pass # Expected on shutdown
    finally:
        unregister_task(search_id)

@router.post("/api/search")
async def start_search(req: SearchRequest):
    search_id = str(uuid.uuid4())
    raw_target = max(100, req.target_count * 4) 
    
    init_progress(search_id, req.target_count, raw_target)
    
    # Start task manually
    task = asyncio.create_task(run_scrape_job_wrapper(search_id, req, raw_target))
    register_task(search_id, task)
    
    # Add defensive done_callback
    task.add_done_callback(lambda t: cleanup_task(search_id, t))
    
    return {"success": True, "search_id": search_id}

@router.get("/api/progress/{search_id}", response_model=ProgressResponse)
async def fetch_progress(search_id: str):
    prog = get_progress(search_id)
    if not prog:
        raise HTTPException(status_code=404, detail="Search ID not found")
    return prog

@router.get("/api/result/{search_id}")
async def fetch_result(search_id: str):
    res = _results_store.get(search_id)
    if not res:
        raise HTTPException(status_code=404, detail="Result not found or not ready")
    return res

@router.post("/api/feedback")
async def handle_feedback(req: FeedbackRequest):
    try:
        save_feedback(req.query, req.product, req.feedback, req.reason)
        return {"success": True, "message": "Feedback saved."}
    except Exception as e:
        log("API", f"Feedback save error: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai/reset")
async def handle_ai_reset():
    success = reset_ai_memory()
    if success:
        return {"success": True, "message": "AI memory reset successfully."}
    raise HTTPException(status_code=500, detail="Failed to reset memory.")

def deduplicate_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_urls = set()
    deduped = []
    for p in products:
        url = p.get("link", p.get("url", ""))
        if url and url not in seen_urls:
            seen_urls.add(url)
            p["link"] = url
            deduped.append(p)
    return deduped

async def run_scrape_job_wrapper(search_id: str, req: SearchRequest, raw_target: int):
    """Wraps the actual job to prevent unhandled background task exceptions."""
    try:
        await run_scrape_job(search_id, req, raw_target)
    except asyncio.CancelledError:
        log(f"[{search_id}]", "Scrape job cancelled (Server shutting down).", "WARN")
        update_progress(search_id, stage="cancelled", done=True, error="Server shutting down, scrape cancelled")
        raise # Reraise for proper task cancellation handling
    except Exception as e:
        tb = traceback.format_exc()
        log(f"[{search_id}]", f"Unhandled exception in background job:\n{tb}", "ERROR")
        fail_progress(search_id, f"Internal Error: {str(e)}")
        safe_save_debug(search_id, error=f"{str(e)}\n{tb}", products=[], progress=get_progress(search_id))
        return

async def run_scrape_job(search_id: str, req: SearchRequest, raw_target: int):
    log(f"[{search_id}]", f"Starting job for '{req.query}' (Target: {req.target_count})", "INFO")
    eta_calc = ETACalculator()
    
    # 1. Scrape raw products
    success, raw_products, error_msg = await run_scraper_chain(search_id, req.query, raw_target, eta_calc)
        
    if not success or not raw_products:
        fail_progress(search_id, error_msg or "Tidak ada produk ditemukan di halaman.")
        return

    # 2. Deduplicate
    update_progress(search_id, stage="deduplicating", percent=70, message="Menghapus duplikat...", elapsed_seconds=eta_calc.get_elapsed())
    deduped = deduplicate_products(raw_products)
    
    # 3. Parse prices and filter budget
    update_progress(search_id, stage="budget_filtering", percent=78, message="Memfilter harga...", elapsed_seconds=eta_calc.get_elapsed())
    budget_valid = []
    
    min_b, max_b = calculate_budget_range(req.budget, req.tolerance)
    
    for p in deduped:
        price_val = p.get("price_val")
        if not price_val:
            price_val = parse_rupiah(p.get("price_text", ""))
        p["price_val"] = price_val
        
        if req.budget and req.budget > 0:
            if min_b <= price_val <= max_b:
                budget_valid.append(p)
        else:
            budget_valid.append(p)
            
    if not budget_valid:
        fail_progress(search_id, "Semua produk ditolak oleh filter budget.")
        return
        
    # 4. AI Relevance Filtering
    update_progress(search_id, stage="ai_filtering", message="Validasi relevansi (AI)...", percent=85, elapsed_seconds=eta_calc.get_elapsed())
    ai_valid = await filter_relevance(req.query, budget_valid, req.use_ai)
    
    if not ai_valid:
        fail_progress(search_id, "Semua produk ditolak oleh AI validator.")
        return
        
    # 5. Finalize
    update_progress(search_id, stage="finalizing", message="Menyiapkan hasil...", percent=95, elapsed_seconds=eta_calc.get_elapsed())
    
    ai_valid.sort(key=lambda x: (-x.get("relevance_score", 0), x.get("price_val", 0)))
    final_list = ai_valid[:req.target_count]
    
    _results_store[search_id] = {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "count": len(final_list),
        "requested_count": req.target_count,
        "data": final_list,
        "budget_info": {
            "budget": req.budget,
            "min": min_b,
            "max": max_b,
            "tolerance": req.tolerance
        } if req.budget else None
    }
    
    complete_progress(search_id)
    log(f"[{search_id}]", f"Job complete. Returned {len(final_list)} products.", "OK")
