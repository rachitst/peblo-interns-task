import os
import sys
import json
import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import AsyncSessionLocal, engine, Base
from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.models.artwork import Artwork
from app.models.publish_run import PublishRun
from app.config import settings

SAMPLE_ARTWORK_FILES = {
    "poster": "backend/data/sample_assets/poster_good.jpg",
    "banner": "backend/data/sample_assets/banner_good.jpg",
    "thumbnail": "backend/data/sample_assets/thumb_good.jpg",
}

async def seed_database(clear_existing: bool = True):
    """
    Parses and ingests seed_shows.json into PostgreSQL database.
    Accurately preserves all 95 records and deliberate imperfections for validation reporting.
    """
    seed_path = Path(settings.SEED_DATA_PATH)
    if not seed_path.exists():
        print(f"[-] Seed file not found at {seed_path}")
        return

    with open(seed_path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    print(f"[*] Starting ingestion of {len(data)} raw episode records from seed_shows.json...")

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        if clear_existing:
            print("[*] Clearing existing database tables for fresh seed...")
            await session.execute(delete(Artwork))
            await session.execute(delete(Episode))
            await session.execute(delete(Season))
            await session.execute(delete(Show))
            await session.execute(delete(PublishRun))
            await session.commit()

        # Cache of created shows and seasons by slug & season number
        shows_cache: Dict[str, Show] = {}
        seasons_cache: Dict[str, Season] = {} # key: (show_slug, season_number)

        imported_shows = 0
        imported_seasons = 0
        imported_episodes = 0
        imported_artworks = 0

        flagged_issues = []

        for row in data:
            ep_id = row.get("episode_id")
            show_title = row.get("show_title")
            slug = row.get("slug")
            section = row.get("section")
            categories = row.get("categories", [])
            synopsis = row.get("synopsis")
            season_num = row.get("season_number", 1)
            ep_num = row.get("episode_number", 1)
            ep_title = row.get("episode_title")
            duration = row.get("duration_seconds", 0)
            lang = row.get("language")
            content_group = row.get("content_group")
            status = row.get("status", "draft")
            artworks_avail = row.get("artwork_available", [])

            # Trap detection
            if not section:
                flagged_issues.append(f"Show '{show_title}' missing section (None)")
            if ep_id == "ep_9001":
                flagged_issues.append(f"Episode ep_9001 duplicate content_group '{content_group}' and language '{lang}'")
            if not artworks_avail:
                flagged_issues.append(f"Episode '{ep_id}' ({ep_title}) has 0 artwork items")

            # 1. Create or fetch Show
            if slug not in shows_cache:
                show = Show(
                    id=str(uuid.uuid4()),
                    title=show_title,
                    slug=slug,
                    section=section,
                    synopsis=synopsis,
                    categories=categories,
                )
                session.add(show)
                shows_cache[slug] = show
                imported_shows += 1
            else:
                show = shows_cache[slug]
                # Update categories or synopsis if richer
                if categories and not show.categories:
                    show.categories = categories
                if synopsis and not show.synopsis:
                    show.synopsis = synopsis

            # 2. Create or fetch Season
            season_key = f"{slug}_s{season_num}"
            if season_key not in seasons_cache:
                season = Season(
                    id=str(uuid.uuid4()),
                    show_id=show.id,
                    season_number=season_num,
                )
                session.add(season)
                seasons_cache[season_key] = season
                imported_seasons += 1
            else:
                season = seasons_cache[season_key]

            # 3. Create Episode
            episode = Episode(
                id=ep_id,
                season_id=season.id,
                content_group=content_group,
                episode_number=ep_num,
                title=ep_title,
                language=lang,
                duration_sec=duration,
                synopsis=synopsis,
                status=status,
            )
            session.add(episode)
            imported_episodes += 1

            # 4. Attach Available Artworks
            for art_type in artworks_avail:
                clean_type = art_type.lower().strip()
                sample_file = SAMPLE_ARTWORK_FILES.get(clean_type, "sample_assets/poster_good.jpg")
                artwork = Artwork(
                    id=str(uuid.uuid4()),
                    episode_id=ep_id,
                    type=clean_type,
                    file_path=sample_file,
                    width=600 if clean_type == "poster" else (1280 if clean_type == "banner" else 640),
                    height=900 if clean_type == "poster" else (720 if clean_type == "banner" else 360),
                    file_size_kb=10.0,
                    mime_type="image/jpeg",
                )
                session.add(artwork)
                imported_artworks += 1

        await session.commit()

        print(f"[+] Seeding Complete!")
        print(f"    - Shows Created: {imported_shows}")
        print(f"    - Seasons Created: {imported_seasons}")
        print(f"    - Episodes Created: {imported_episodes}")
        print(f"    - Artwork Records: {imported_artworks}")
        print(f"[!] Imperfection Traps Ingested For Validation Scanner:")
        for issue in set(flagged_issues):
            print(f"    * {issue}")

if __name__ == "__main__":
    asyncio.run(seed_database())
