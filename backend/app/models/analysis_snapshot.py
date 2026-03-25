from sqlalchemy import Integer, Float, ForeignKey, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import Optional
from app.models.base import Base, TimestampMixin


class AnalysisSnapshot(Base, TimestampMixin):
    __tablename__ = "analysis_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("brand_monitors.id"), index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    total_posts: Mapped[int] = mapped_column(Integer, default=0)
    total_comments: Mapped[int] = mapped_column(Integer, default=0)
    avg_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_distribution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    top_topics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    hot_posts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    subreddit_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    marketing_advice: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    monitor = relationship("BrandMonitor", back_populates="snapshots")
