from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./reddit_marketing.db"
    database_url_sync: str = "sqlite:///./reddit_marketing.db"

    # Redis (optional)
    redis_url: str = ""

    # Reddit API (optional, using public JSON API)
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "RedditMarketingTool/1.0"

    # Gemini API
    gemini_api_key: str = ""

    # JWT Auth
    jwt_secret_key: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""

    # Frontend URL (for Stripe redirects)
    frontend_url: str = "http://localhost:3000"

    # CORS allowed origins (comma separated)
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # App
    app_name: str = "RedditPulse"
    debug: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
