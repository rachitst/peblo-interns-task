from app.routers.admin_shows import router as admin_shows_router
from app.routers.admin_upload import router as admin_upload_router
from app.routers.admin_publish import router as admin_publish_router
from app.routers.viewer_catalog import router as viewer_catalog_router

__all__ = [
    "admin_shows_router",
    "admin_upload_router",
    "admin_publish_router",
    "viewer_catalog_router",
]
