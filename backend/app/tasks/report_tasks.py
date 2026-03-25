import os
from app.tasks.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models.analysis_snapshot import AnalysisSnapshot
from app.models.report import Report
from app.services.report_generator import ReportGenerator
from sqlalchemy import select, update


REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


@celery_app.task(bind=True, name="app.tasks.report_tasks.generate_report_task")
def generate_report_task(self, report_id: int, snapshot_id: int, report_type: str, keyword: str):
    """Generate a report file from an analysis snapshot."""
    db = SyncSessionLocal()
    try:
        # Fetch snapshot data
        result = db.execute(
            select(AnalysisSnapshot).where(AnalysisSnapshot.id == snapshot_id)
        )
        snapshot = result.scalar_one_or_none()
        if not snapshot:
            db.execute(
                update(Report).where(Report.id == report_id).values(status="failed")
            )
            db.commit()
            return {"status": "error", "message": "Snapshot not found"}

        # Build report data
        report_data = {
            "keyword": keyword,
            "date": str(snapshot.snapshot_date),
            "total_posts": snapshot.total_posts,
            "total_comments": snapshot.total_comments,
            "avg_sentiment": snapshot.avg_sentiment,
            "sentiment_distribution": snapshot.sentiment_distribution,
            "top_topics": snapshot.top_topics,
            "hot_posts": snapshot.hot_posts,
            "subreddit_breakdown": snapshot.subreddit_breakdown,
            "marketing_advice": snapshot.marketing_advice,
        }

        # Generate file
        generator = ReportGenerator()
        filename = f"reddit_{keyword}_{snapshot.snapshot_date}_{report_id}"

        if report_type == "pdf":
            filepath = generator.generate_pdf(report_data, REPORTS_DIR, filename)
        elif report_type == "pptx":
            filepath = generator.generate_pptx(report_data, REPORTS_DIR, filename)
        elif report_type == "docx":
            filepath = generator.generate_docx(report_data, REPORTS_DIR, filename)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Update report record
        db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(status="completed", file_path=filepath)
        )
        db.commit()

        return {"status": "completed", "file_path": filepath}

    except Exception as e:
        db.execute(
            update(Report).where(Report.id == report_id).values(status="failed")
        )
        db.commit()
        raise e
    finally:
        db.close()
