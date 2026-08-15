import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routers import (
    admin_shows_router,
    admin_upload_router,
    admin_publish_router,
    viewer_catalog_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure storage folders exist
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.PUBLISHED_DIR).mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown: Dispose DB connection pool
    await engine.dispose()

app = FastAPI(
    title="Peblo TV Mini Core API",
    description="3-tier streaming catalogue system API: Internal CMS management, publishing pipeline, and Netflix-style viewer catalogue.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directories for local storage assets
storage_root = Path(settings.UPLOAD_DIR).parent
if storage_root.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_root)), name="storage")

sample_assets_dir = Path(__file__).resolve().parent.parent / "data" / "sample_assets"
if sample_assets_dir.exists():
    app.mount("/sample_assets", StaticFiles(directory=str(sample_assets_dir)), name="sample_assets")

# Include Routers
app.include_router(admin_shows_router)
app.include_router(admin_upload_router)
app.include_router(admin_publish_router)
app.include_router(viewer_catalog_router)

@app.get("/health", tags=["System Health"])
async def health_check():
    """
    Comprehensive service health check:
    - Verifies PostgreSQL database connectivity
    - Verifies storage directory read/write capability
    """
    db_status = "healthy"
    db_error = None
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)

    storage_status = "healthy"
    if not (os.path.exists(settings.UPLOAD_DIR) and os.path.exists(settings.PUBLISHED_DIR)):
        storage_status = "degraded"

    overall_status = "healthy" if db_status == "healthy" and storage_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "database": db_status,
        "database_error": db_error,
        "storage": storage_status,
        "environment": settings.APP_ENV,
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Peblo TV Mini Core API",
        "docs": "/docs",
        "health": "/health",
        "viewer_catalog": "/catalog",
        "admin_validation": "/admin/validation-report",
    }
