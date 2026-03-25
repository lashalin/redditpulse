from __future__ import annotations

import uuid
import threading
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from pydantic import BaseModel
from typing import Optional

from app.database import get_db, SyncSessionLocal
from app.models.user import User
from app.models.brand_monitor import BrandMonitor, MonitorStatus
from app.models.post import Post
from app.models.analysis_snapshot import AnalysisSnapshot
from app.api.auth import get_current_user
from app.services.analyzer import BrandAnalyzer

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# In-memory task tracker (simple replacement for Celery)
_task_status: dict[str, dict] = {}


# Schemas
class AnalysisRequest(BaseModel):
    keyword: str
    time_range: str = "3m"


class QuickAnalysisResponse(BaseModel):
    task_id: str
    status: str
    message: str


class SnapshotResponse(BaseModel):
    id: int
    monitor_id: int
    snapshot_date: str
    total_posts: int
    total_comments: int
    avg_sentiment: Optional[float] = None
    sentiment_distribution: Optional[dict] = None
    top_topics: Optional[dict] = None
    hot_posts: Optional[dict] = None
    subreddit_breakdown: Optional[dict] = None
    marketing_advice: Optional[dict] = None


def _run_analysis_in_background(task_id: str, monitor_id: int, keyword: str, time_range: str):
    """Run analysis in a background thread (replaces Celery)."""
    db = SyncSessionLocal()
    try:
        _task_status[task_id] = {"status": "CRAWLING", "result": None}

        # Update monitor status
        db.execute(
            update(BrandMonitor)
            .where(BrandMonitor.id == monitor_id)
            .values(status=MonitorStatus.CRAWLING)
        )
        db.commit()

        # Run analysis
        analyzer = BrandAnalyzer()
        results = analyzer.run_full_analysis(keyword, time_range=time_range)

        if "error" in results:
            _task_status[task_id] = {"status": "FAILURE", "result": results["error"]}
            db.execute(
                update(BrandMonitor)
                .where(BrandMonitor.id == monitor_id)
                .values(status=MonitorStatus.ACTIVE)
            )
            db.commit()
            return

        _task_status[task_id] = {"status": "ANALYZING", "result": None}

        # Update status to analyzing
        db.execute(
            update(BrandMonitor)
            .where(BrandMonitor.id == monitor_id)
            .values(status=MonitorStatus.ANALYZING)
        )
        db.commit()

        # Save posts to database
        for post_data in results["posts"]:
            existing = db.execute(
                select(Post).where(Post.reddit_id == post_data["reddit_id"])
            ).scalar_one_or_none()

            if not existing:
                post = Post(
                    monitor_id=monitor_id,
                    reddit_id=post_data["reddit_id"],
                    subreddit=post_data["subreddit"],
                    title=post_data["title"],
                    body=post_data.get("body"),
                    author=post_data.get("author"),
                    url=post_data["url"],
                    score=post_data["score"],
                    upvote_ratio=post_data.get("upvote_ratio"),
                    num_comments=post_data["num_comments"],
                    created_utc=post_data["created_utc"] if isinstance(post_data["created_utc"], datetime) else datetime.fromisoformat(post_data["created_utc"]),
                    sentiment_label=post_data.get("sentiment_label"),
                    sentiment_score=post_data.get("sentiment_score"),
                )
                db.add(post)
            else:
                existing.score = post_data["score"]
                existing.num_comments = post_data["num_comments"]
                existing.sentiment_label = post_data.get("sentiment_label")
                existing.sentiment_score = post_data.get("sentiment_score")

        db.commit()

        # Save analysis snapshot
        stats = results["stats"]
        snapshot = AnalysisSnapshot(
            monitor_id=monitor_id,
            snapshot_date=date.today(),
            total_posts=stats["total_posts"],
            total_comments=0,
            avg_sentiment=stats["sentiment"]["avg_score"],
            sentiment_distribution=stats["sentiment"],
            top_topics={"raw": results["analysis"]["topic_clusters"]},
            hot_posts={"raw": results["analysis"]["hot_posts_summary"]},
            subreddit_breakdown={
                "profiles": results["analysis"]["subreddit_profiles"],
                "data": results["subreddits"],
            },
            marketing_advice={"raw": results["analysis"]["marketing_advice"]},
        )
        db.add(snapshot)

        # Update monitor
        db.execute(
            update(BrandMonitor)
            .where(BrandMonitor.id == monitor_id)
            .values(
                status=MonitorStatus.ACTIVE,
                total_posts=stats["total_posts"],
                last_crawled_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        _task_status[task_id] = {
            "status": "SUCCESS",
            "result": {
                "monitor_id": monitor_id,
                "total_posts": stats["total_posts"],
            },
        }

    except Exception as e:
        db.rollback()
        _task_status[task_id] = {"status": "FAILURE", "result": str(e)}
        db.execute(
            update(BrandMonitor)
            .where(BrandMonitor.id == monitor_id)
            .values(status=MonitorStatus.ACTIVE)
        )
        db.commit()
        print(f"Analysis error: {e}")
    finally:
        db.close()


# Routes
@router.post("/run", response_model=QuickAnalysisResponse)
async def trigger_analysis(
    data: AnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a full brand analysis."""
    # Check quota
    if user.monthly_analysis_used >= user.monthly_analysis_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly limit reached ({user.monthly_analysis_limit}). Upgrade plan.",
        )

    # Find or create monitor
    result = await db.execute(
        select(BrandMonitor).where(
            BrandMonitor.user_id == user.id,
            BrandMonitor.keyword == data.keyword,
        )
    )
    monitor = result.scalar_one_or_none()

    if not monitor:
        monitor = BrandMonitor(
            user_id=user.id,
            keyword=data.keyword,
            time_range=data.time_range,
            status=MonitorStatus.CRAWLING,
        )
        db.add(monitor)
        await db.flush()
        await db.refresh(monitor)
    else:
        monitor.status = MonitorStatus.CRAWLING
        await db.flush()

    # Increment usage
    user.monthly_analysis_used += 1
    await db.flush()

    # Run analysis in background thread
    task_id = str(uuid.uuid4())
    thread = threading.Thread(
        target=_run_analysis_in_background,
        args=(task_id, monitor.id, data.keyword, data.time_range),
        daemon=True,
    )
    thread.start()

    return QuickAnalysisResponse(
        task_id=task_id,
        status="processing",
        message=f"Analysis started for '{data.keyword}'. Check back in 1-2 minutes.",
    )


@router.get("/status/{task_id}")
async def check_task_status(task_id: str):
    """Check the status of an analysis task."""
    status = _task_status.get(task_id, {"status": "UNKNOWN", "result": None})
    return {
        "task_id": task_id,
        "status": status["status"],
        "result": status["result"],
    }


@router.get("/snapshot/{monitor_id}", response_model=Optional[SnapshotResponse])
async def get_latest_snapshot(
    monitor_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest analysis snapshot for a monitor."""
    result = await db.execute(
        select(BrandMonitor).where(
            BrandMonitor.id == monitor_id,
            BrandMonitor.user_id == user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Monitor not found")

    result = await db.execute(
        select(AnalysisSnapshot)
        .where(AnalysisSnapshot.monitor_id == monitor_id)
        .order_by(desc(AnalysisSnapshot.snapshot_date))
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No analysis results yet")

    return SnapshotResponse(
        id=snapshot.id,
        monitor_id=snapshot.monitor_id,
        snapshot_date=str(snapshot.snapshot_date),
        total_posts=snapshot.total_posts,
        total_comments=snapshot.total_comments,
        avg_sentiment=snapshot.avg_sentiment,
        sentiment_distribution=snapshot.sentiment_distribution,
        top_topics=snapshot.top_topics,
        hot_posts=snapshot.hot_posts,
        subreddit_breakdown=snapshot.subreddit_breakdown,
        marketing_advice=snapshot.marketing_advice,
    )


@router.get("/snapshots/{monitor_id}", response_model=list[SnapshotResponse])
async def list_snapshots(
    monitor_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all analysis snapshots for a monitor."""
    result = await db.execute(
        select(BrandMonitor).where(
            BrandMonitor.id == monitor_id,
            BrandMonitor.user_id == user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Monitor not found")

    result = await db.execute(
        select(AnalysisSnapshot)
        .where(AnalysisSnapshot.monitor_id == monitor_id)
        .order_by(desc(AnalysisSnapshot.snapshot_date))
    )
    snapshots = result.scalars().all()
    return [
        SnapshotResponse(
            id=s.id, monitor_id=s.monitor_id,
            snapshot_date=str(s.snapshot_date),
            total_posts=s.total_posts, total_comments=s.total_comments,
            avg_sentiment=s.avg_sentiment,
            sentiment_distribution=s.sentiment_distribution,
            top_topics=s.top_topics, hot_posts=s.hot_posts,
            subreddit_breakdown=s.subreddit_breakdown,
            marketing_advice=s.marketing_advice,
        )
        for s in snapshots
    ]
