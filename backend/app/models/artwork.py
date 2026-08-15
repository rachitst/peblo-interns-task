import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.episode import Episode

class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    episode_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # poster, banner, thumbnail
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_kb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    episode: Mapped["Episode"] = relationship(back_populates="artworks")

    __table_args__ = (
        UniqueConstraint("episode_id", "type", name="uq_episode_artwork_type"),
    )
