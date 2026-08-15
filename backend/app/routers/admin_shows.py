import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.models.artwork import Artwork
from app.schemas.show import (
    ShowCreate,
    ShowUpdate,
    ShowResponse,
    SeasonCreate,
    SeasonResponse,
    EpisodeCreate,
    EpisodeUpdate,
    EpisodeResponse,
)
from app.routers.auth import require_roles

router = APIRouter(prefix="/admin", tags=["Admin CMS - Shows & Content"])

# ----------------- SHOWS -----------------

@router.get("/shows", response_model=List[ShowResponse])
async def list_shows(
    section: Optional[str] = Query(None, description="Filter by section"),
    search: Optional[str] = Query(None, description="Search by title or synopsis"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = (
        select(Show)
        .options(
            selectinload(Show.seasons)
            .selectinload(Season.episodes)
            .selectinload(Episode.artworks)
        )
        .order_by(Show.title)
    )

    if section:
        stmt = stmt.where(Show.section == section)
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Show.title.ilike(search_pattern),
                Show.synopsis.ilike(search_pattern),
                Show.slug.ilike(search_pattern),
            )
        )

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/shows/{show_id}", response_model=ShowResponse)
async def get_show(
    show_id: str,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = (
        select(Show)
        .options(
            selectinload(Show.seasons)
            .selectinload(Season.episodes)
            .selectinload(Episode.artworks)
        )
        .where(or_(Show.id == show_id, Show.slug == show_id))
    )
    result = await db.execute(stmt)
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=404, detail=f"Show '{show_id}' not found.")
    return show

@router.post("/shows", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
async def create_show(
    payload: ShowCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    # Check duplicate slug
    existing = (
        await db.execute(select(Show).where(Show.slug == payload.slug))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Show with slug '{payload.slug}' already exists."
        )

    show = Show(
        id=payload.id or str(uuid.uuid4()),
        title=payload.title,
        slug=payload.slug,
        section=payload.section,
        synopsis=payload.synopsis,
        categories=payload.categories,
    )
    db.add(show)
    await db.commit()
    await db.refresh(show)
    return show

@router.patch("/shows/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: str,
    payload: ShowUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = (
        select(Show)
        .options(
            selectinload(Show.seasons)
            .selectinload(Season.episodes)
            .selectinload(Episode.artworks)
        )
        .where(Show.id == show_id)
    )
    result = await db.execute(stmt)
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=404, detail=f"Show '{show_id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] != show.slug:
        slug_check = (
            await db.execute(select(Show).where(Show.slug == update_data["slug"]))
        ).scalar_one_or_none()
        if slug_check:
            raise HTTPException(
                status_code=400,
                detail=f"Show with slug '{update_data['slug']}' already exists.",
            )

    for field, val in update_data.items():
        setattr(show, field, val)

    await db.commit()
    await db.refresh(show)
    return show

@router.delete("/shows/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    show_id: str,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["admin"])), # Only admin can delete whole show
):
    stmt = select(Show).where(Show.id == show_id)
    result = await db.execute(stmt)
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=404, detail=f"Show '{show_id}' not found.")

    await db.delete(show)
    await db.commit()
    return None

# ----------------- SEASONS -----------------

@router.post("/shows/{show_id}/seasons", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
async def create_season(
    show_id: str,
    payload: SeasonCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    show = (await db.execute(select(Show).where(Show.id == show_id))).scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=404, detail=f"Show '{show_id}' not found.")

    season = Season(
        id=payload.id or str(uuid.uuid4()),
        show_id=show_id,
        season_number=payload.season_number,
    )
    db.add(season)
    await db.commit()
    await db.refresh(season)
    return season

# ----------------- EPISODES -----------------

@router.get("/episodes", response_model=List[EpisodeResponse])
async def list_episodes(
    status: Optional[str] = Query(None, description="Filter by status (draft, published)"),
    language: Optional[str] = Query(None, description="Filter by language"),
    search: Optional[str] = Query(None, description="Search title or content_group"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = (
        select(Episode)
        .options(selectinload(Episode.artworks))
        .order_by(Episode.id)
    )

    if status:
        stmt = stmt.where(Episode.status == status)
    if language:
        stmt = stmt.where(Episode.language == language)
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Episode.title.ilike(search_pattern),
                Episode.content_group.ilike(search_pattern),
                Episode.id.ilike(search_pattern),
            )
        )

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/episodes/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: str,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = (
        select(Episode)
        .options(selectinload(Episode.artworks))
        .where(Episode.id == episode_id)
    )
    result = await db.execute(stmt)
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found.")
    return episode

@router.post("/seasons/{season_id}/episodes", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_episode(
    season_id: str,
    payload: EpisodeCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    season = (await db.execute(select(Season).where(Season.id == season_id))).scalar_one_or_none()
    if not season:
        raise HTTPException(status_code=404, detail=f"Season '{season_id}' not found.")

    # Rule: (content_group, language) uniqueness check
    dup = (
        await db.execute(
            select(Episode).where(
                Episode.content_group == payload.content_group,
                Episode.language == payload.language,
            )
        )
    ).scalar_one_or_none()
    if dup:
        raise HTTPException(
            status_code=400,
            detail=f"An episode with content_group '{payload.content_group}' and language '{payload.language}' already exists (ID: {dup.id}).",
        )

    # Generate episode ID if not provided
    ep_id = payload.id or f"ep_{uuid.uuid4().hex[:8]}"

    episode = Episode(
        id=ep_id,
        season_id=season_id,
        content_group=payload.content_group,
        episode_number=payload.episode_number,
        title=payload.title,
        language=payload.language,
        duration_sec=payload.duration_sec,
        synopsis=payload.synopsis,
        status=payload.status,
    )
    db.add(episode)
    await db.commit()
    await db.refresh(episode)
    return episode

@router.patch("/episodes/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_id: str,
    payload: EpisodeUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = (
        select(Episode)
        .options(selectinload(Episode.artworks))
        .where(Episode.id == episode_id)
    )
    result = await db.execute(stmt)
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)

    # Validate unique content_group + language if modified
    new_cg = update_data.get("content_group", episode.content_group)
    new_lang = update_data.get("language", episode.language)
    if (new_cg != episode.content_group or new_lang != episode.language):
        dup = (
            await db.execute(
                select(Episode).where(
                    Episode.content_group == new_cg,
                    Episode.language == new_lang,
                    Episode.id != episode.id,
                )
            )
        ).scalar_one_or_none()
        if dup:
            raise HTTPException(
                status_code=400,
                detail=f"Conflict: (content_group='{new_cg}', language='{new_lang}') is already used by episode {dup.id}.",
            )

    # Rule: can't publish without duration > 0 and artworks
    if update_data.get("status") == "published":
        eff_duration = update_data.get("duration_sec", episode.duration_sec)
        if eff_duration <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot publish episode '{episode.title}': duration must be greater than 0 seconds.",
            )

    for field, val in update_data.items():
        setattr(episode, field, val)

    await db.commit()
    await db.refresh(episode)
    return episode

@router.delete("/episodes/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    episode_id: str,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    stmt = select(Episode).where(Episode.id == episode_id)
    result = await db.execute(stmt)
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail=f"Episode '{episode_id}' not found.")

    await db.delete(episode)
    await db.commit()
    return None
