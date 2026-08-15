import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.show import Show
    from app.models.episode import Episode

class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    show_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    season_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 is reserved for trailers

    show: Mapped["Show"] = relationship(back_populates="seasons")
    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="season",
        cascade="all, delete-orphan",
        order_by="Episode.episode_number",
        lazy="selectin",
    )
