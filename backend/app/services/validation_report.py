from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.show import Show
from app.models.season import Season
from app.models.episode import Episode
from app.models.artwork import Artwork
from app.schemas.validation import ValidationIssue, ValidationReportResponse

REQUIRED_ARTWORK_TYPES = {"poster", "banner", "thumbnail"}
ALLOWED_SECTIONS = {"featured", "series", "minisodes", "songs"}

class ValidationReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(self) -> ValidationReportResponse:
        """
        Scans all shows, seasons, episodes, and artworks in the database to identify
        all blocking issues and warnings preventing a successful catalogue publication.
        """
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

        issues: List[ValidationIssue] = []
        grouped_by_show: Dict[str, List[ValidationIssue]] = {}

        # 1. Global check: duplicate (content_group, language)
        cg_stmt = (
            select(Episode.content_group, Episode.language, func.count(Episode.id).label("cnt"))
            .group_by(Episode.content_group, Episode.language)
            .having(func.count(Episode.id) > 1)
        )
        cg_res = await self.db.execute(cg_stmt)
        duplicates = cg_res.all()
        for cg, lang, count in duplicates:
            # Find the offending episodes
            dup_ep_stmt = select(Episode).where(Episode.content_group == cg, Episode.language == lang)
            dup_eps = (await self.db.execute(dup_ep_stmt)).scalars().all()
            ep_ids = [e.id for e in dup_eps]
            issue = ValidationIssue(
                entity_type="episode",
                entity_id=", ".join(ep_ids),
                show_title="Cross-Show / Global Conflict",
                severity="blocker",
                code="DUPLICATE_CONTENT_GROUP_LANGUAGE",
                message=f"Duplicate content group '{cg}' with language '{lang}' found across episodes: {', '.join(ep_ids)} ({count} occurrences).",
                fix_suggestion="Ensure each content_group has at most one episode per language. Reassign or rename content_group.",
            )
            issues.append(issue)
            grouped_by_show.setdefault("Global Conflicts", []).append(issue)

        # 2. Show & Episode Level Checks
        for show in shows:
            show_key = show.title or show.id

            # Rule: Show must have a section
            if not show.section:
                issue = ValidationIssue(
                    entity_type="show",
                    entity_id=show.id,
                    show_id=show.id,
                    show_title=show.title,
                    severity="blocker",
                    code="SHOW_MISSING_SECTION",
                    message=f"Show '{show.title}' has no section assigned (must be one of: {', '.join(sorted(ALLOWED_SECTIONS))}).",
                    fix_suggestion="Assign a valid section ('featured', 'series', 'minisodes', 'songs') in Show Settings.",
                )
                issues.append(issue)
                grouped_by_show.setdefault(show_key, []).append(issue)
            elif show.section.lower() not in ALLOWED_SECTIONS:
                issue = ValidationIssue(
                    entity_type="show",
                    entity_id=show.id,
                    show_id=show.id,
                    show_title=show.title,
                    severity="blocker",
                    code="SHOW_INVALID_SECTION",
                    message=f"Show '{show.title}' has invalid section '{show.section}'. Allowed: {', '.join(sorted(ALLOWED_SECTIONS))}.",
                    fix_suggestion=f"Update section to one of: {', '.join(sorted(ALLOWED_SECTIONS))}.",
                )
                issues.append(issue)
                grouped_by_show.setdefault(show_key, []).append(issue)

            # Check if show has any episodes
            total_show_eps = sum(len(s.episodes) for s in show.seasons)
            published_show_eps = sum(
                len([e for e in s.episodes if e.status == "published"]) for s in show.seasons
            )
            if total_show_eps == 0:
                issue = ValidationIssue(
                    entity_type="show",
                    entity_id=show.id,
                    show_id=show.id,
                    show_title=show.title,
                    severity="warning",
                    code="SHOW_NO_EPISODES",
                    message=f"Show '{show.title}' does not contain any seasons or episodes.",
                    fix_suggestion="Create at least one season and episode before publishing.",
                )
                issues.append(issue)
                grouped_by_show.setdefault(show_key, []).append(issue)
            elif published_show_eps == 0:
                issue = ValidationIssue(
                    entity_type="show",
                    entity_id=show.id,
                    show_id=show.id,
                    show_title=show.title,
                    severity="warning",
                    code="SHOW_NO_PUBLISHED_EPISODES",
                    message=f"Show '{show.title}' has {total_show_eps} draft episode(s) but 0 published episodes.",
                    fix_suggestion="Publish at least one episode to include this show in the viewer catalogue.",
                )
                issues.append(issue)
                grouped_by_show.setdefault(show_key, []).append(issue)

            # Inspect Seasons & Episodes
            for season in show.seasons:
                is_trailer_season = (season.season_number == 0)

                for ep in season.episodes:
                    if ep.status != "published":
                        continue

                    # Check Duration
                    if ep.duration_sec <= 0:
                        issue = ValidationIssue(
                            entity_type="episode",
                            entity_id=ep.id,
                            show_id=show.id,
                            show_title=show.title,
                            season_number=season.season_number,
                            episode_id=ep.id,
                            episode_number=ep.episode_number,
                            severity="blocker",
                            code="EPISODE_MISSING_DURATION",
                            message=f"Episode '{ep.title}' ({ep.id}) has a duration of 0 seconds.",
                            fix_suggestion="Specify a valid runtime duration in seconds.",
                        )
                        issues.append(issue)
                        grouped_by_show.setdefault(show_key, []).append(issue)

                    # Check Artwork
                    available_art_types = {art.type for art in ep.artworks}
                    
                    # For normal episodes, poster, banner, and thumbnail are expected
                    if is_trailer_season:
                        # Trailers must have at least thumbnail or banner
                        if not available_art_types:
                            issue = ValidationIssue(
                                entity_type="episode",
                                entity_id=ep.id,
                                show_id=show.id,
                                show_title=show.title,
                                season_number=season.season_number,
                                episode_id=ep.id,
                                episode_number=ep.episode_number,
                                severity="blocker",
                                code="TRAILER_MISSING_ARTWORK",
                                message=f"Trailer '{ep.title}' ({ep.id}) has no artwork uploaded.",
                                fix_suggestion="Upload at least a thumbnail or banner for the trailer.",
                            )
                            issues.append(issue)
                            grouped_by_show.setdefault(show_key, []).append(issue)
                    else:
                        missing_arts = REQUIRED_ARTWORK_TYPES - available_art_types
                        if missing_arts:
                            issue = ValidationIssue(
                                entity_type="episode",
                                entity_id=ep.id,
                                show_id=show.id,
                                show_title=show.title,
                                season_number=season.season_number,
                                episode_id=ep.id,
                                episode_number=ep.episode_number,
                                severity="blocker",
                                code="EPISODE_MISSING_ARTWORK",
                                message=f"Episode '{ep.title}' ({ep.id}) is missing artwork: {', '.join(sorted(missing_arts))}.",
                                fix_suggestion=f"Upload the missing {', '.join(sorted(missing_arts))} image(s) conforming to dimensions.",
                            )
                            issues.append(issue)
                            grouped_by_show.setdefault(show_key, []).append(issue)

        total_blockers = len([i for i in issues if i.severity == "blocker"])
        total_warnings = len([i for i in issues if i.severity == "warning"])
        can_publish = (total_blockers == 0)

        summary = (
            "Catalogue is ready to publish."
            if can_publish
            else f"Publishing blocked by {total_blockers} issue(s) across {len(grouped_by_show)} show(s)."
        )

        return ValidationReportResponse(
            can_publish=can_publish,
            total_blockers=total_blockers,
            total_warnings=total_warnings,
            summary=summary,
            issues=issues,
            grouped_by_show=grouped_by_show,
        )
