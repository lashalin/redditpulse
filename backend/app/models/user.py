from sqlalchemy import String, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.models.base import Base, TimestampMixin


class PlanTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(100))
    plan_tier: Mapped[PlanTier] = mapped_column(
        SAEnum(PlanTier), default=PlanTier.FREE
    )
    monthly_analysis_limit: Mapped[int] = mapped_column(Integer, default=3)
    monthly_analysis_used: Mapped[int] = mapped_column(Integer, default=0)

    # Stripe
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)

    # Relationships
    brand_monitors = relationship("BrandMonitor", back_populates="user")
    reports = relationship("Report", back_populates="user")
