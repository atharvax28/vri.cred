"""API routes — all endpoints for the VRI MSME Credit Scoring System.

Routes:
- GET  /health             → System health check
- GET  /api/v1/gstins      → List available demo GSTINs
- GET  /api/v1/gstins/{id} → Get GSTIN details
- POST /api/v1/score       → Score a GSTIN (returns score + SHAP)
- POST /api/v1/report      → Generate full credit memo with Claude
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import (
    CreditMemoResponse,
    ErrorResponse,
    GSTINDetailResponse,
    GSTINListResponse,
    HealthResponse,
    ScoreRequest,
    ScoreResponse,
    ShapFactorResponse,
)
from src.core.exceptions import AppError, GSTINNotFoundError
from src.core.logging import logger
from src.reports.generator import ReportGenerator
from src.scoring.features import extract_features
from src.scoring.model import CreditScoringModel
from src.scoring.pipeline import run_scoring_pipeline
from src.scoring.repositories import MockGSTINRepository

# ── Global singletons (initialized in main.py lifespan) ──
_repository: MockGSTINRepository | None = None
_model: CreditScoringModel | None = None
_report_gen: ReportGenerator | None = None


def init_dependencies(
    repo: MockGSTINRepository,
    model: CreditScoringModel,
    report_gen: ReportGenerator,
) -> None:
    """Called once during app startup."""
    global _repository, _model, _report_gen
    _repository = repo
    _model = model
    _report_gen = report_gen


def get_repo() -> MockGSTINRepository:
    assert _repository is not None, "Repository not initialized"
    return _repository


def get_model() -> CreditScoringModel:
    assert _model is not None, "Model not initialized"
    return _model


def get_report_gen() -> ReportGenerator:
    assert _report_gen is not None, "Report generator not initialized"
    return _report_gen


# ── Router ──
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    model = get_model()
    return HealthResponse(
        status="ok" if model.is_ready else "degraded",
        model_ready=model.is_ready,
        version="1.0.0-demo",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/api/v1/gstins",
    response_model=GSTINListResponse,
    tags=["GSTIN"],
    summary="List Demo GSTINs",
)
async def list_gstins():
    """List all available demo GSTINs for testing."""
    repo = get_repo()
    gstins = await repo.list_available()
    return GSTINListResponse(gstins=gstins, count=len(gstins))


@router.get(
    "/api/v1/gstins/{gstin}",
    response_model=GSTINDetailResponse,
    tags=["GSTIN"],
    summary="Get GSTIN Details",
    responses={404: {"model": ErrorResponse}},
)
async def get_gstin_detail(gstin: str):
    """Fetch detailed data for a specific GSTIN."""
    repo = get_repo()
    try:
        data = await repo.fetch(gstin.upper())
    except GSTINNotFoundError:
        raise HTTPException(status_code=404, detail=f"GSTIN {gstin} not found in demo data")

    return GSTINDetailResponse(**asdict(data))


@router.post(
    "/api/v1/score",
    response_model=ScoreResponse,
    tags=["Scoring"],
    summary="Score GSTIN",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def score_gstin(request: ScoreRequest):
    """Score a GSTIN — returns VRI score, risk grade, PD, and SHAP explanations."""
    repo = get_repo()
    model = get_model()

    try:
        result, data = await run_scoring_pipeline(
            gstin=request.gstin.upper(),
            repository=repo,
            model=model,
        )
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return ScoreResponse(
        gstin=data.gstin,
        legal_name=data.legal_name,
        trade_name=data.trade_name,
        vri_score=result.vri_score,
        risk_grade=result.risk_grade,
        probability_of_default=result.probability_of_default,
        shap_factors=[
            ShapFactorResponse(
                feature=f.feature,
                display_name=f.display_name,
                value=f.value,
                shap_value=f.shap_value,
                direction=f.direction,
                magnitude=f.magnitude,
            )
            for f in result.shap_factors
        ],
        model_version=result.model_version,
    )


@router.post(
    "/api/v1/report",
    response_model=CreditMemoResponse,
    tags=["Reports"],
    summary="Generate Credit Memo",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_report(request: ScoreRequest):
    """Score + generate a full AI-powered credit memo.

    If Anthropic API key is set, uses Claude for narrative generation.
    Otherwise, falls back to a template-based report.
    """
    repo = get_repo()
    model = get_model()
    report_gen = get_report_gen()

    try:
        scoring_result, gstin_data = await run_scoring_pipeline(
            gstin=request.gstin.upper(),
            repository=repo,
            model=model,
        )
        memo = await report_gen.generate(scoring_result, gstin_data)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return CreditMemoResponse(
        gstin=memo.gstin,
        legal_name=memo.legal_name,
        trade_name=memo.trade_name,
        vri_score=memo.vri_score,
        risk_grade=memo.risk_grade,
        probability_of_default=memo.probability_of_default,
        executive_summary=memo.executive_summary,
        business_overview=memo.business_overview,
        financial_analysis=memo.financial_analysis,
        risk_factors=memo.risk_factors,
        strengths=memo.strengths,
        recommendation=memo.recommendation,
        shap_top_factors=memo.shap_top_factors,
        model_version=memo.model_version,
        generated_at=memo.generated_at,
        disclaimer=memo.disclaimer,
    )
