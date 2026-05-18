"""
main.py - FastAPI application setup.
Mounts API routes and serves the frontend.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from src.server.routes import router

# Initialize FastAPI
app = FastAPI(
    title="Tokopedia Scraper API",
    description="Python/Playwright scraper with Qwen AI validation.",
    version="4.0"
)

# Include API routes
app.include_router(router)

# Basic health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Serve Frontend
# Assuming web files are in the 'web' directory at project root
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
        # Catch all for serving css/js directly from root if asked
        file_path = WEB_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        # Fallback to index.html for SPA if needed, or 404
        index_path = WEB_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Not found"}

else:
    @app.get("/")
    async def serve_index_fallback():
        return {"error": "Web directory missing"}
