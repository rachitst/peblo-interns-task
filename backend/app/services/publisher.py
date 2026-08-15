import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.models.artwork import Artwork
from app.models.publish_run import PublishRun
from app.services.storage import get_storage
from app.config import settings

SECTION_ORDER = ["featured", "series", "minisodes", "songs"]

class PublishService:
    def __init__(self, db: AsyncSession, storage = None):
        self.db = db
        self.storage = storage or get_storage()

    async def generate_and_publish_catalogue(
        self, published_by: str = "admin@peblo.tv"
    ) -> Dict[str, Any]:
        """
        Builds the entire catalogue JSON structure in-memory and atomically writes it
        to storage. A record of the publish run is persisted in the PostgreSQL database.
        """
        # Load all shows with seasons, episodes, and artworks
        stmt = (
            select(Show)
            .options(
                selectinload(Show.seasons)
                .selectinload(Season.episodes)
                .selectinload(Episode.artworks)
            )
            .order_by(Show.title)
        )
        result = await self.db.execute(stmt)
        shows = result.scalars().all()

        sections_map: Dict[str, List[Dict[str, Any]]] = {
            sec: [] for sec in SECTION_ORDER
        }
        # Catch-all for other sections
        other_sections: Dict[str, List[Dict[str, Any]]] = {}

        total_published_shows = 0
        total_published_episodes = 0

        for show in shows:
            # Rule: Published show must have a section
            if not show.section:
                continue

            show_artworks: Dict[str, Optional[str]] = {
                "poster": None,
                "banner": None,
                "thumbnail": None,
            }
            show_trailers: List[Dict[str, Any]] = []
            catalogue_seasons: List[Dict[str, Any]] = []
            show_episode_count = 0

            # Sort seasons deterministically
            sorted_seasons = sorted(show.seasons, key=lambda s: s.season_number)

            for season in sorted_seasons:
                # Season 0 is reserved for trailers
                if season.season_number == 0:
                    for ep in season.episodes:
                        if ep.status == "published":
                            trailer_arts = {
                                art.type: self.storage.get_url(art.file_path)
                                for art in ep.artworks
                            }
                            # Populate show artwork fallback if empty
                            for k, v in trailer_arts.items():
                                if not show_artworks.get(k):
                                    show_artworks[k] = v

                            show_trailers.append({
                                "episode_id": ep.id,
                                "title": ep.title,
                                "language": ep.language,
                                "duration_sec": ep.duration_sec,
                                "artworks": trailer_arts,
                            })
                    continue

                # Normal seasons: Group episodes by content_group
                published_eps = [
                    ep for ep in season.episodes if ep.status == "published"
                ]
                if not published_eps:
                    continue

                # Group by content_group to collapse multi-language variants
                content_groups: Dict[str, List[Episode]] = {}
                for ep in published_eps:
                    content_groups.setdefault(ep.content_group, []).append(ep)

                collapsed_episodes: List[Dict[str, Any]] = []

                # Deterministic sort by episode number of the first variant
                sorted_groups = sorted(
                    content_groups.values(),
                    key=lambda group: min(e.episode_number for e in group),
                )

                for group in sorted_groups:
                    # Pick primary episode variant (e.g. English first, or first item)
                    primary_ep = next((e for e in group if e.language == "en"), group[0])
                    available_languages = sorted(list(set(e.language for e in group)))

                    # Aggregate artworks across group variants
                    group_artworks: Dict[str, Optional[str]] = {
                        "poster": None,
                        "banner": None,
                        "thumbnail": None,
                    }
                    for ep in group:
                        for art in ep.artworks:
                            if not group_artworks.get(art.type):
                                group_artworks[art.type] = self.storage.get_url(art.file_path)

                    # Update show artwork defaults
                    for k, v in group_artworks.items():
                        if not show_artworks.get(k) and v:
                            show_artworks[k] = v

                    variants_list = [
                        {
                            "episode_id": ep.id,
                            "language": ep.language,
                            "title": ep.title,
                            "duration_sec": ep.duration_sec,
                            "synopsis": ep.synopsis,
                        }
                        for ep in sorted(group, key=lambda e: e.language)
                    ]

                    collapsed_episodes.append({
                        "content_group": primary_ep.content_group,
                        "episode_number": primary_ep.episode_number,
                        "title": primary_ep.title,
                        "duration_sec": primary_ep.duration_sec,
                        "synopsis": primary_ep.synopsis,
                        "languages": available_languages,
                        "artworks": group_artworks,
                        "variants": variants_list,
                    })
                    show_episode_count += 1
                    total_published_episodes += 1

                if collapsed_episodes:
                    catalogue_seasons.append({
                        "season_number": season.season_number,
                        "episodes": collapsed_episodes,
                    })

            # Only include show if it has published episodes or trailers
            if catalogue_seasons or show_trailers:
                show_payload = {
                    "id": show.id,
                    "title": show.title,
                    "slug": show.slug,
                    "section": show.section,
                    "categories": show.categories or [],
                    "synopsis": show.synopsis,
                    "artworks": show_artworks,
                    "trailers": show_trailers,
                    "seasons": catalogue_seasons,
                    "total_episodes": show_episode_count,
                }

                sec_key = show.section.lower()
                if sec_key in sections_map:
                    sections_map[sec_key].append(show_payload)
                else:
                    other_sections.setdefault(sec_key, []).append(show_payload)
                
                total_published_shows += 1

        # Merge other sections into final output
        final_sections = {**sections_map, **other_sections}

        # Build published catalogue envelope
        now_utc = datetime.now(timezone.utc)
        catalogue_data = {
            "version": int(now_utc.timestamp()),
            "generated_at": now_utc.isoformat(),
            "generated_by": published_by,
            "total_shows": total_published_shows,
            "total_episodes": total_published_episodes,
            "sections": final_sections,
        }

        # Atomic file write to published directory
        published_file_name = "catalogue.json"
        saved_file_path = await self.storage.atomic_write_json(
            published_file_name, catalogue_data
        )

        # Record publish run in DB
        publish_run = PublishRun(
            published_at=now_utc,
            published_by=published_by,
            status="success",
            catalogue_version=catalogue_data["version"],
            shows_count=total_published_shows,
            episodes_count=total_published_episodes,
            file_path=saved_file_path,
            metadata_json={
                "section_counts": {k: len(v) for k, v in final_sections.items()},
                "published_file": published_file_name,
            },
        )
        self.db.add(publish_run)
        await self.db.commit()
        await self.db.refresh(publish_run)

        return {
            "run_id": publish_run.id,
            "status": "success",
            "published_at": now_utc.isoformat(),
            "published_by": published_by,
            "catalogue_version": catalogue_data["version"],
            "shows_count": total_published_shows,
            "episodes_count": total_published_episodes,
            "file_path": saved_file_path,
            "catalogue": catalogue_data,
        }
