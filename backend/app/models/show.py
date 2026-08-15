import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.season import Season

class Show(Base):
    __tablename__ = "shows"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    section: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True) # featured, series, minisodes, songs
    synopsis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categories: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    seasons: Mapped[List["Season"]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
        order_by="Season.season_number",
        lazy="selectin",
    )
