from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict

class CatalogueArtworkMap(BaseModel):
    poster: Optional[str] = None
    banner: Optional[str] = None
    thumbnail: Optional[str] = None

class CatalogueEpisodeVariant(BaseModel):
    episode_id: str
    language: str
    title: str
    duration_sec: int
    synopsis: Optional[str] = None

class CatalogueEpisodeItem(BaseModel):
    content_group: str
    episode_number: int
    title: str
    duration_sec: int
    synopsis: Optional[str] = None
    languages: List[str]
    artworks: CatalogueArtworkMap = CatalogueArtworkMap()
    variants: List[CatalogueEpisodeVariant] = []

class CatalogueTrailerItem(BaseModel):
    episode_id: str
    title: str
    language: str
    duration_sec: int
    artworks: CatalogueArtworkMap = CatalogueArtworkMap()

class CatalogueSeasonItem(BaseModel):
    season_number: int
    episodes: List[CatalogueEpisodeItem] = []

class CatalogueShowItem(BaseModel):
    id: str
    title: str
    slug: str
    section: str
    categories: List[str]
    synopsis: Optional[str] = None
    artworks: CatalogueArtworkMap = CatalogueArtworkMap()
    trailers: List[CatalogueTrailerItem] = []
    seasons: List[CatalogueSeasonItem] = []
    total_episodes: int = 0

class PublishedCatalogue(BaseModel):
    version: int
    generated_at: str
    generated_by: str
    total_shows: int
    total_episodes: int
    sections: Dict[str, List[CatalogueShowItem]]

    model_config = ConfigDict(from_attributes=True)

class CatalogSearchResponse(BaseModel):
    query: str
    matched_shows_count: int
    matched_episodes_count: int
    results: List[CatalogueShowItem]
