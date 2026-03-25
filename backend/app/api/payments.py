"""Stripe payment integration for Pro plan subscriptions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.config import get_settings
from app.database import get_db
from app.models.user import User, PlanTier
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["payments"])
settings = get_settings()


@router.post("/create-checkout")
async def create_checkout_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Checkout session for Pro plan upgrade."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="支付功能暂未开通")

    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key

        checkout = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{
                "price": settings.stripe_pro_price_id,
                "quantity": 1,
            }],
            success_url=f"{settings.frontend_url}/dashboard?upgraded=true",
            cancel_url=f"{settings.frontend_url}/dashboard?cancelled=true",
            client_reference_id=str(user.id),
            customer_email=user.email,
            metadata={"user_id": str(user.id)},
        )
        return {"checkout_url": checkout.url, "session_id": checkout.id}
    except ImportError:
        raise HTTPException(status_code=503, detail="Stripe SDK未安装")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    import stripe
    stripe.api_key = settings.stripe_secret_key

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
        if user_id:
            await db.execute(
                update(User)
                .where(User.id == int(user_id))
                .values(
                    plan_tier=PlanTier.PRO,
                    monthly_analysis_limit=9999,
                    stripe_customer_id=session.get("customer", ""),
                    stripe_subscription_id=session.get("subscription", ""),
                )
            )

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer", "")
        if customer_id:
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.plan_tier = PlanTier.FREE
                user.monthly_analysis_limit = 3
                user.stripe_subscription_id = None

    return {"status": "ok"}


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_user),
):
    """Get user's current subscription status."""
    return {
        "plan": user.plan_tier.value,
        "limit": user.monthly_analysis_limit,
        "used": user.monthly_analysis_used,
        "stripe_customer_id": getattr(user, "stripe_customer_id", None),
    }
