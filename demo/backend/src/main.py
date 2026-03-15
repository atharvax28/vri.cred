"""Main FastAPI application — entrypoint for `uvicorn src.main:app`.

Startup sequence:
1. Train/load XGBoost model
2. Initialize repositories
3. Mount routes
4. Start serving
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import init_dependencies, router
from src.core.config import get_settings
from src.core.logging import logger
from src.reports.generator import ReportGenerator
from src.scoring.model import CreditScoringModel
from src.scoring.repositories import MockGSTINRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown hooks."""
    settings = get_settings()
    logger.info("Starting VRI MSME Credit Scoring System...")

    # Initialize scoring model
    model = CreditScoringModel()
    if not model.load_model():
        model.train_demo_model()

    # Initialize repository and report generator
    repo = MockGSTINRepository()
    report_gen = ReportGenerator()

    # Wire up dependencies
    init_dependencies(repo, model, report_gen)

    logger.info("System ready. API available at http://%s:%d", settings.host, settings.port)
    logger.info("API docs at http://%s:%d/docs", settings.host, settings.port)

    yield

    logger.info("Shutting down VRI MSME Credit Scoring System.")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title="VRI MSME Credit Scoring System",
        description=(
            "AI-powered credit scoring for Indian MSMEs using GST data, "
            "XGBoost ML models, and Claude-powered narrative reports. "
            "Demo mode — uses synthetic data."
        ),
        version="1.0.0-demo",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    cors_origins = settings.cors_origin_list
    # Allow all Vercel deployments in production
    if any("vercel.app" in o for o in cors_origins):
        cors_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount all routes
    app.include_router(router)

    return app


app = create_app()
