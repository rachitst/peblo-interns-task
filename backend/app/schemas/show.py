from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

ArtworkType = Literal["poster", "banner", "thumbnail"]
EpisodeStatus = Literal["draft", "published"]

class ArtworkBase(BaseModel):
    type: ArtworkType
    file_path: str
    width: Optional[int] = None
    height: Optional[int] = None
    file_size_kb: Optional[float] = None
    mime_type: Optional[str] = None

class ArtworkResponse(ArtworkBase):
    id: str
    episode_id: str
    created_at: datetime
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EpisodeBase(BaseModel):
    content_group: str = Field(..., description="Unique episode group across language variants")
    episode_number: int = Field(..., ge=0)
    title: str = Field(..., min_length=1)
    language: str = Field(..., min_length=2, max_length=10)
    duration_sec: int = Field(0, ge=0)
    synopsis: Optional[str] = None
    status: EpisodeStatus = "draft"

class EpisodeCreate(EpisodeBase):
    id: Optional[str] = None

class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    content_group: Optional[str] = None
    episode_number: Optional[int] = None
    language: Optional[str] = None
    duration_sec: Optional[int] = None
    synopsis: Optional[str] = None
    status: Optional[EpisodeStatus] = None

class EpisodeResponse(EpisodeBase):
    id: str
    season_id: str
    created_at: datetime
    updated_at: datetime
    artworks: List[ArtworkResponse] = []

    model_config = ConfigDict(from_attributes=True)

class SeasonBase(BaseModel):
    season_number: int = Field(..., ge=0, description="0 is reserved for trailers")

class SeasonCreate(SeasonBase):
    id: Optional[str] = None

class SeasonResponse(SeasonBase):
    id: str
    show_id: str
    episodes: List[EpisodeResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ShowBase(BaseModel):
    title: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    section: Optional[str] = Field(None, description="featured, series, minisodes, songs")
    synopsis: Optional[str] = None
    categories: List[str] = []

class ShowCreate(ShowBase):
    id: Optional[str] = None

class ShowUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    section: Optional[str] = None
    synopsis: Optional[str] = None
    categories: Optional[List[str]] = None

class ShowResponse(ShowBase):
    id: str
    created_at: datetime
    updated_at: datetime
    seasons: List[SeasonResponse] = []

    model_config = ConfigDict(from_attributes=True)
