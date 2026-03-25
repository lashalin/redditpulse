from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.models.base import Base, TimestampMixin


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("brand_monitors.id"), index=True)
    reddit_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    subreddit: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    url: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, default=0)
    upvote_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    num_comments: Mapped[int] = mapped_column(Integer, default=0)
    created_utc: Mapped[datetime] = mapped_column(index=True)

    # Sentiment
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    monitor = relationship("BrandMonitor", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
