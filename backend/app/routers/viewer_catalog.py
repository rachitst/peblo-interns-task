import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.storage import get_storage
from app.schemas.catalog import PublishedCatalogue, CatalogSearchResponse, CatalogueShowItem

router = APIRouter(prefix="/catalog", tags=["Viewer - Published Catalogue"])

async def load_published_catalogue_data() -> Dict[str, Any]:
    """Reads the current published catalogue.json from storage."""
    storage = get_storage()
    cat_path = Path(settings.PUBLISHED_DIR) / "catalogue.json"
    if not cat_path.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Catalogue has not been published yet. Please publish the catalogue from the Admin CMS.",
        )
    
    try:
        content = await storage.get_file(str(cat_path))
        return json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read published catalogue: {str(e)}",
        )

@router.get("", response_model=PublishedCatalogue)
async def get_published_catalogue():
    """
    Returns the latest atomically published catalogue file for the Netflix-style viewer UI.
    """
    return await load_published_catalogue_data()

@router.get("/search", response_model=CatalogSearchResponse)
async def search_catalogue(
    q: Optional[str] = Query(None, description="Search query matching show title, episode title, or category"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. adventure, science)"),
    language: Optional[str] = Query(None, description="Filter by available language (e.g. en, hi)"),
    section: Optional[str] = Query(None, description="Filter by section (e.g. featured, series)"),
):
    """
    Fast composed search & filter over the published catalogue:
    - `q` matches across show titles, episode titles, and categories.
    - All filters compose conjunctively (AND).
    """
    cat_data = await load_published_catalogue_data()
    all_shows: List[Dict[str, Any]] = []

    # Flatten shows across all sections
    sections = cat_data.get("sections", {})
    seen_show_ids = set()
    for sec_name, show_list in sections.items():
        if section and sec_name.lower() != section.lower():
            continue
        for show in show_list:
            if show["id"] not in seen_show_ids:
                seen_show_ids.add(show["id"])
                all_shows.append(show)

    query_str = (q or "").lower().strip()
    category_filter = (category or "").lower().strip()
    language_filter = (language or "").lower().strip()

    filtered_shows: List[Dict[str, Any]] = []
    matched_episodes_count = 0

    for show in all_shows:
        # Category Filter
        show_categories = [c.lower() for c in show.get("categories", [])]
        if category_filter and category_filter not in show_categories:
            continue

        # Language Filter
        show_languages = set()
        for s in show.get("seasons", []):
            for ep in s.get("episodes", []):
                for lang in ep.get("languages", []):
                    show_languages.add(lang.lower())
        for tr in show.get("trailers", []):
            if tr.get("language"):
                show_languages.add(tr["language"].lower())

        if language_filter and language_filter not in show_languages:
            continue

        # Query Filter (matches show title, synopsis, categories, or episode titles)
        if query_str:
            show_title_match = query_str in show.get("title", "").lower()
            synopsis_match = query_str in (show.get("synopsis") or "").lower()
            category_match = any(query_str in c for c in show_categories)
            
            # Check episode matches
            ep_matches = []
            for s in show.get("seasons", []):
                for ep in s.get("episodes", []):
                    if query_str in ep.get("title", "").lower() or query_str in (ep.get("synopsis") or "").lower():
                        ep_matches.append(ep)

            if show_title_match or synopsis_match or category_match or ep_matches:
                matched_episodes_count += len(ep_matches)
                filtered_shows.append(show)
        else:
            filtered_shows.append(show)

    return CatalogSearchResponse(
        query=q or "",
        matched_shows_count=len(filtered_shows),
        matched_episodes_count=matched_episodes_count,
        results=filtered_shows,
    )

@router.get("/shows/{show_id_or_slug}", response_model=CatalogueShowItem)
async def get_catalogue_show_detail(show_id_or_slug: str):
    """
    Returns single show details from the published catalogue including trailer metadata
    and collapsed multi-language episode options.
    """
    cat_data = await load_published_catalogue_data()
    sections = cat_data.get("sections", {})

    for sec_name, show_list in sections.items():
        for show in show_list:
            if show["id"] == show_id_or_slug or show["slug"] == show_id_or_slug:
                return show

    raise HTTPException(
        status_code=404,
        detail=f"Show '{show_id_or_slug}' not found in published catalogue.",
    )
