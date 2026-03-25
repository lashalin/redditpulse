from sqlalchemy import String, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum
from app.models.base import Base, TimestampMixin


class ReportType(str, enum.Enum):
    PDF = "pdf"
    PPTX = "pptx"
    DOCX = "docx"


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("brand_monitors.id"), index=True)
    snapshot_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("analysis_snapshots.id"), nullable=True
    )
    report_type: Mapped[ReportType] = mapped_column(SAEnum(ReportType))
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="generating")

    # Relationships
    user = relationship("User", back_populates="reports")
