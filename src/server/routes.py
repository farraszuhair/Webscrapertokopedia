"""
routes.py - FastAPI routes for the scraping API.
"""
import uuid
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from src.server.schemas import SearchRequest, FeedbackRequest, ProgressResponse
from src.server.progress import init_progress, get_progress, update_progress, complete_progress, fail_progress
from src.utils.logger import log
from src.utils.currency import calculate_budget_range, parse_rupiah
from src.utils.eta import ETACalculator
from src.scraper.engine import PlaywrightEngine
from src.ai.relevance import filter_relevance
from src.ai.learning import save_feedback
from src.ai.reset import reset_ai_memory

router = APIRouter()

# Store final results here so frontend can poll them if needed
# In a real app, this goes to DB. For now, memory is fine.
_results_store: Dict[str, Dict[str, Any]] = {}

@router.post("/api/search")
async def start_search(req: SearchRequest, background_tasks: BackgroundTasks):
    search_id = str(uuid.uuid4())
    raw_target = max(100, req.target_count * 4) # Overfetch heavily for AI filtering
    
    # Init progress
    init_progress(search_id, req.target_count, raw_target)
    
    # Start background job
    background_tasks.add_task(run_scrape_job, search_id, req, raw_target)
    
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

# ---------------------------------------------------------
# BACKGROUND WORKER
# ---------------------------------------------------------

def deduplicate_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates by URL and Name."""
    seen_urls = set()
    deduped = []
    for p in products:
        url = p.get("link", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(p)
    return deduped

async def run_scrape_job(search_id: str, req: SearchRequest, raw_target: int):
    log(f"[{search_id}]", f"Starting job for '{req.query}' (Target: {req.target_count})", "INFO")
    eta_calc = ETACalculator()
    
    # 1. Scrape raw products
    engine = PlaywrightEngine(search_id)
    try:
        raw_products = await engine.scrape(req.query, raw_target, eta_calc)
    except Exception as e:
        fail_progress(search_id, str(e))
        return
    finally:
        await engine.close()
        
    if not raw_products:
        fail_progress(search_id, "Tidak ada produk ditemukan di halaman.")
        return

    # 2. Deduplicate
    update_progress(search_id, stage="deduplicating", message="Menghapus duplikat...")
    deduped = deduplicate_products(raw_products)
    
    # 3. Parse prices and filter budget
    update_progress(search_id, stage="filtering_budget", message="Memfilter harga...")
    budget_valid = []
    min_b, max_b = calculate_budget_range(req.budget, req.tolerance)
    
    for p in deduped:
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
    update_progress(search_id, stage="ai_filtering", message="Validasi relevansi (AI)...", percent=80)
    ai_valid = await filter_relevance(req.query, budget_valid, req.use_ai)
    
    if not ai_valid:
        fail_progress(search_id, "Semua produk ditolak oleh AI validator.")
        return
        
    # 5. Finalize
    update_progress(search_id, stage="finalizing", message="Menyiapkan hasil...", percent=95)
    
    # Sort by relevance and then by price
    ai_valid.sort(key=lambda x: (-x.get("relevance_score", 0), x.get("price_val", 0)))
    final_list = ai_valid[:req.target_count]
    
    # Store result
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
    
    # Done
    complete_progress(search_id)
    log(f"[{search_id}]", f"Job complete. Returned {len(final_list)} products.", "OK")
