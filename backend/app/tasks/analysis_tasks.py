from datetime import date, datetime, timezone
from app.tasks.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models.brand_monitor import BrandMonitor, MonitorStatus
from app.models.post import Post
from app.models.comment import Comment
from app.models.analysis_snapshot import AnalysisSnapshot
from app.models.user import User
from app.services.analyzer import BrandAnalyzer
from sqlalchemy import select, update


@celery_app.task(bind=True, name="app.tasks.analysis_tasks.run_brand_analysis_task")
def run_brand_analysis_task(self, monitor_id: int, keyword: str, time_range: str, user_id: int):
    """Run full brand analysis pipeline as a Celery task."""
    db = SyncSessionLocal()
    try:
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
            db.execute(
                update(BrandMonitor)
                .where(BrandMonitor.id == monitor_id)
                .values(status=MonitorStatus.ACTIVE)
            )
            db.commit()
            return {"status": "error", "message": results["error"]}

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
                    created_utc=datetime.fromisoformat(post_data["created_utc"]) if isinstance(post_data["created_utc"], str) else post_data["created_utc"],
                    sentiment_label=post_data.get("sentiment_label"),
                    sentiment_score=post_data.get("sentiment_score"),
                )
                db.add(post)
            else:
                # Update dynamic fields
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

        return {
            "status": "completed",
            "monitor_id": monitor_id,
            "total_posts": stats["total_posts"],
            "sentiment": stats["sentiment"],
        }

    except Exception as e:
        db.rollback()
        # Reset status on error
        db.execute(
            update(BrandMonitor)
            .where(BrandMonitor.id == monitor_id)
            .values(status=MonitorStatus.ACTIVE)
        )
        db.commit()
        raise e
    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.daily_incremental_crawl")
def daily_incremental_crawl():
    """Daily crawl for all active monitors."""
    db = SyncSessionLocal()
    try:
        result = db.execute(
            select(BrandMonitor).where(BrandMonitor.status == MonitorStatus.ACTIVE)
        )
        monitors = result.scalars().all()

        for monitor in monitors:
            run_brand_analysis_task.delay(
                monitor_id=monitor.id,
                keyword=monitor.keyword,
                time_range="1m",  # Only recent posts for daily crawl
                user_id=monitor.user_id,
            )
    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.weekly_full_refresh")
def weekly_full_refresh():
    """Weekly full refresh for all active monitors."""
    db = SyncSessionLocal()
    try:
        result = db.execute(
            select(BrandMonitor).where(BrandMonitor.status == MonitorStatus.ACTIVE)
        )
        monitors = result.scalars().all()

        for monitor in monitors:
            run_brand_analysis_task.delay(
                monitor_id=monitor.id,
                keyword=monitor.keyword,
                time_range=monitor.time_range.value,
                user_id=monitor.user_id,
            )
    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.reset_monthly_quotas")
def reset_monthly_quotas():
    """Reset all users' monthly analysis counters."""
    db = SyncSessionLocal()
    try:
        db.execute(update(User).values(monthly_analysis_used=0))
        db.commit()
    finally:
        db.close()
