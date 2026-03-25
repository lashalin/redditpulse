from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.brand_monitor import BrandMonitor, MonitorStatus, TimeRange
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


# Schemas
class MonitorCreate(BaseModel):
    keyword: str
    time_range: str = "3m"


class MonitorResponse(BaseModel):
    id: int
    keyword: str
    time_range: str
    status: str
    total_posts: int
    last_crawled_at: Optional[str] = None

    class Config:
        from_attributes = True


# Routes
@router.post("", response_model=MonitorResponse)
async def create_monitor(
    data: MonitorCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check quota
    if user.monthly_analysis_used >= user.monthly_analysis_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly analysis limit reached ({user.monthly_analysis_limit}). Upgrade your plan.",
        )

    # Check duplicate
    result = await db.execute(
        select(BrandMonitor).where(
            BrandMonitor.user_id == user.id,
            BrandMonitor.keyword == data.keyword,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Monitor already exists for this keyword")

    monitor = BrandMonitor(
        user_id=user.id,
        keyword=data.keyword,
        time_range=TimeRange(data.time_range),
        status=MonitorStatus.ACTIVE,
    )
    db.add(monitor)
    await db.flush()
    await db.refresh(monitor)

    return MonitorResponse(
        id=monitor.id,
        keyword=monitor.keyword,
        time_range=monitor.time_range.value,
        status=monitor.status.value,
        total_posts=monitor.total_posts,
        last_crawled_at=str(monitor.last_crawled_at) if monitor.last_crawled_at else None,
    )


@router.get("", response_model=list[MonitorResponse])
async def list_monitors(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BrandMonitor).where(BrandMonitor.user_id == user.id)
    )
    monitors = result.scalars().all()
    return [
        MonitorResponse(
            id=m.id, keyword=m.keyword, time_range=m.time_range.value,
            status=m.status.value, total_posts=m.total_posts,
            last_crawled_at=str(m.last_crawled_at) if m.last_crawled_at else None,
        )
        for m in monitors
    ]


@router.delete("/{monitor_id}")
async def delete_monitor(
    monitor_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BrandMonitor).where(
            BrandMonitor.id == monitor_id,
            BrandMonitor.user_id == user.id,
        )
    )
    monitor = result.scalar_one_or_none()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    await db.delete(monitor)
    return {"status": "deleted"}
