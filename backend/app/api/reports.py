from __future__ import annotations

import threading
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from pydantic import BaseModel
from typing import Optional

from app.database import get_db, SyncSessionLocal
from app.models.user import User
from app.models.brand_monitor import BrandMonitor
from app.models.analysis_snapshot import AnalysisSnapshot
from app.models.report import Report, ReportType
from app.api.auth import get_current_user
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportRequest(BaseModel):
    monitor_id: int
    report_type: str  # "pdf", "pptx", "docx"


class ReportResponse(BaseModel):
    id: int
    monitor_id: int
    report_type: str
    status: str
    file_path: Optional[str] = None


def _generate_report_in_background(report_id: int, snapshot_id: int, report_type: str, keyword: str):
    """Generate report in background thread."""
    db = SyncSessionLocal()
    try:
        # Get snapshot data
        snapshot = db.execute(
            select(AnalysisSnapshot).where(AnalysisSnapshot.id == snapshot_id)
        ).scalar_one_or_none()

        if not snapshot:
            db.execute(update(Report).where(Report.id == report_id).values(status="failed"))
            db.commit()
            return

        # Build report data
        report_data = {
            "keyword": keyword,
            "snapshot_date": str(snapshot.snapshot_date),
            "total_posts": snapshot.total_posts,
            "total_comments": snapshot.total_comments,
            "avg_sentiment": snapshot.avg_sentiment,
            "sentiment_distribution": snapshot.sentiment_distribution or {},
            "top_topics": snapshot.top_topics or {},
            "hot_posts": snapshot.hot_posts or {},
            "subreddit_breakdown": snapshot.subreddit_breakdown or {},
            "marketing_advice": snapshot.marketing_advice or {},
        }

        # Generate report
        generator = ReportGenerator()
        if report_type == "pptx":
            file_path = generator.generate_pptx(report_data, keyword)
        elif report_type == "docx":
            file_path = generator.generate_docx(report_data, keyword)
        else:
            file_path = generator.generate_pdf(report_data, keyword)

        # Update report record
        db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(status="completed", file_path=file_path)
        )
        db.commit()

    except Exception as e:
        db.execute(update(Report).where(Report.id == report_id).values(status="failed"))
        db.commit()
        print(f"Report generation error: {e}")
    finally:
        db.close()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    data: ReportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a report in the specified format."""
    # Verify monitor ownership
    result = await db.execute(
        select(BrandMonitor).where(
            BrandMonitor.id == data.monitor_id,
            BrandMonitor.user_id == user.id,
        )
    )
    monitor = result.scalar_one_or_none()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    # Get latest snapshot
    result = await db.execute(
        select(AnalysisSnapshot)
        .where(AnalysisSnapshot.monitor_id == data.monitor_id)
        .order_by(desc(AnalysisSnapshot.snapshot_date))
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No analysis data. Run analysis first.")

    # Create report record
    report = Report(
        user_id=user.id,
        monitor_id=data.monitor_id,
        snapshot_id=snapshot.id,
        report_type=ReportType(data.report_type),
        status="generating",
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    # Run in background thread
    thread = threading.Thread(
        target=_generate_report_in_background,
        args=(report.id, snapshot.id, data.report_type, monitor.keyword),
        daemon=True,
    )
    thread.start()

    return ReportResponse(
        id=report.id,
        monitor_id=data.monitor_id,
        report_type=data.report_type,
        status="generating",
    )


@router.get("/status/{report_id}", response_model=ReportResponse)
async def check_report_status(
    report_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check report generation status."""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse(
        id=report.id,
        monitor_id=report.monitor_id,
        report_type=report.report_type.value,
        status=report.status,
        file_path=report.file_path,
    )


@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    token: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a generated report."""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.status != "completed" or not report.file_path:
        raise HTTPException(status_code=400, detail=f"Report status: {report.status}")

    media_types = {
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return FileResponse(
        report.file_path,
        media_type=media_types.get(report.report_type.value, "application/octet-stream"),
        filename=f"reddit_analysis_{report.id}.{report.report_type.value}",
    )
