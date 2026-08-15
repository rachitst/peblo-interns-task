from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.season import Season
    from app.models.artwork import Artwork

class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True) # e.g. ep_0001
    season_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_group: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, index=True) # en, hi
    duration_sec: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True) # draft, published

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    season: Mapped["Season"] = relationship(back_populates="episodes")
    artworks: Mapped[List["Artwork"]] = relationship(
        back_populates="episode",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_episodes_content_group_lang", "content_group", "language"),
        Index("ix_episodes_content_group_status", "content_group", "status"),
    )
