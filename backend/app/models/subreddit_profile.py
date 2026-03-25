from sqlalchemy import String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.models.base import Base, TimestampMixin


class SubredditProfile(Base, TimestampMixin):
    __tablename__ = "subreddit_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("brand_monitors.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    subscriber_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    top_topics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    community_vibe: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    marketing_friendliness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    monitor = relationship("BrandMonitor", back_populates="subreddit_profiles")
