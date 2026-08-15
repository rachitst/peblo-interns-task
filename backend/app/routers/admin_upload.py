import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path as FPath, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.episode import Episode
from app.models.artwork import Artwork
from app.schemas.show import ArtworkResponse
from app.services.storage import get_storage
from app.services.image_validator import validate_artwork_image, ImageValidationError
from app.routers.auth import require_roles

router = APIRouter(prefix="/admin", tags=["Admin CMS - Artwork Uploads"])

@router.post("/episodes/{episode_id}/artwork/{artwork_type}", response_model=ArtworkResponse)
async def upload_artwork(
    episode_id: str = FPath(..., description="Episode ID, e.g. ep_0001"),
    artwork_type: str = FPath(..., description="poster, banner, or thumbnail"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    """
    Validates uploaded image specs (dimensions, aspect ratio, 200KB ceiling) via Pillow,
    persists bytes via storage abstraction, and updates/creates the episode's Artwork record.
    """
    clean_type = artwork_type.lower().strip()
    if clean_type not in {"poster", "banner", "thumbnail"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid artwork type '{artwork_type}'. Allowed types: poster, banner, thumbnail.",
        )

    # Check episode exists
    ep_stmt = select(Episode).where(Episode.id == episode_id)
    episode = (await db.execute(ep_stmt)).scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found.")

    # Read bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Pillow validation
    try:
        meta = validate_artwork_image(file_bytes, clean_type)
    except ImageValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Image validation failed",
                "message": e.message,
                "details": e.details,
            },
        )

    # Save to storage
    storage = get_storage()
    ext = Path(file.filename or f"image.{meta['format'].lower()}").suffix or f".{meta['format'].lower()}"
    destination_path = f"episodes/{episode_id}/{clean_type}_{uuid.uuid4().hex[:6]}{ext}"
    saved_path = await storage.save_file(file_bytes, destination_path)

    # Update or create Artwork record
    art_stmt = select(Artwork).where(
        Artwork.episode_id == episode_id, Artwork.type == clean_type
    )
    existing_art = (await db.execute(art_stmt)).scalar_one_or_none()

    if existing_art:
        # Delete old file if local
        await storage.delete_file(existing_art.file_path)
        existing_art.file_path = saved_path
        existing_art.width = meta["width"]
        existing_art.height = meta["height"]
        existing_art.file_size_kb = meta["file_size_kb"]
        existing_art.mime_type = meta["mime_type"]
        artwork_record = existing_art
    else:
        artwork_record = Artwork(
            id=str(uuid.uuid4()),
            episode_id=episode_id,
            type=clean_type,
            file_path=saved_path,
            width=meta["width"],
            height=meta["height"],
            file_size_kb=meta["file_size_kb"],
            mime_type=meta["mime_type"],
        )
        db.add(artwork_record)

    await db.commit()
    await db.refresh(artwork_record)

    response_data = ArtworkResponse.model_validate(artwork_record)
    response_data.url = storage.get_url(artwork_record.file_path)
    return response_data
