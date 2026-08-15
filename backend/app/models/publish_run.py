import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class PublishRun(Base):
    __tablename__ = "publish_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    published_by: Mapped[str] = mapped_column(String(100), default="admin@peblo.tv", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="success", nullable=False, index=True) # success, failed
    catalogue_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    shows_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    episodes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
