"""
main.py - FastAPI application setup.
Mounts API routes and serves the frontend.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from src.server.routes import router
from src.server.lifecycle import cancel_all_tasks
from src.utils.logger import log

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.ai.feedback_store import ensure_feedback_db
    from src.ai.model_registry import get_orchestrator_status

    ensure_feedback_db()
    get_orchestrator_status(force_refresh=True)
    yield
    log("SERVER", "Shutting down, cleaning up...", "INFO")
    await cancel_all_tasks()

# Initialize FastAPI
app = FastAPI(
    title="Tokopedia Scraper API",
    description="Python/Puppeteer/Selenium scraper with automatic local AI orchestration.",
    version="4.0",
    lifespan=lifespan
)

# No-cache middleware for HTML/CSS/JS
@app.middleware("http")
async def no_cache_frontend(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".html", ".css", ".js")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Include API routes
app.include_router(router)

# Basic health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Serve Frontend
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
WEB_DIR = PROJECT_DIR / "web"

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        index_path = WEB_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Frontend not built or web/index.html missing"}
        
    @app.get("/{path:path}")
    async def serve_static(path: str):
        file_path = WEB_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        index_path = WEB_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Not found"}

else:
    @app.get("/")
    async def serve_index_fallback():
        return {"error": "Web directory missing"}
