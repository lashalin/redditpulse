from sqlalchemy import String, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import enum
from app.models.base import Base, TimestampMixin


class MonitorStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CRAWLING = "crawling"
    ANALYZING = "analyzing"


class TimeRange(str, enum.Enum):
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"
    ALL_TIME = "all"


class BrandMonitor(Base, TimestampMixin):
    __tablename__ = "brand_monitors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    keyword: Mapped[str] = mapped_column(String(200), index=True)
    time_range: Mapped[TimeRange] = mapped_column(
        SAEnum(TimeRange), default=TimeRange.THREE_MONTHS
    )
    status: Mapped[MonitorStatus] = mapped_column(
        SAEnum(MonitorStatus), default=MonitorStatus.ACTIVE
    )
    last_crawled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    total_posts: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="brand_monitors")
    posts = relationship("Post", back_populates="monitor", cascade="all, delete-orphan")
    snapshots = relationship("AnalysisSnapshot", back_populates="monitor", cascade="all, delete-orphan")
    subreddit_profiles = relationship("SubredditProfile", back_populates="monitor", cascade="all, delete-orphan")
