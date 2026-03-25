from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.models.base import Base, TimestampMixin


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    reddit_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    body: Mapped[str] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_utc: Mapped[datetime] = mapped_column()

    # Sentiment
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    post = relationship("Post", back_populates="comments")
