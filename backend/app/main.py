from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.api import auth, monitor, analysis, reports
from app.api import payments
from app.database import sync_engine
from app.models import Base
import os

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=sync_engine)
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    print("Database tables created")
    print(f"RedditPulse API is running!")
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered Reddit brand sentiment analysis tool",
    lifespan=lifespan,
    redirect_slashes=False,
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve exported reports as static files
if os.path.exists("reports"):
    app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Register routers
app.include_router(auth.router)
app.include_router(monitor.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(payments.router)


@app.get("/")
async def root():
    return {"message": "RedditPulse API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
