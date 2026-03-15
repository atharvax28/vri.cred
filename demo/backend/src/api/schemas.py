"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Request Schemas ──

class ScoreRequest(BaseModel):
    """Request to score a GSTIN."""
    gstin: str = Field(
        ...,
        min_length=15,
        max_length=15,
        pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$",
        description="15-character alphanumeric GSTIN",
        examples=["27AABCM1234D1Z5"],
    )


# ── Response Schemas ──

class ShapFactorResponse(BaseModel):
    feature: str
    display_name: str
    value: float
    shap_value: float
    direction: Literal["positive", "negative"]
    magnitude: Literal["high", "medium", "low"]


class ScoreResponse(BaseModel):
    """Complete scoring response."""
    gstin: str
    legal_name: str
    trade_name: str
    vri_score: int = Field(ge=0, le=1000)
    risk_grade: str
    probability_of_default: float = Field(ge=0.0, le=1.0)
    shap_factors: list[ShapFactorResponse]
    model_version: str


class CreditMemoResponse(BaseModel):
    """Complete credit memo response."""
    gstin: str
    legal_name: str
    trade_name: str
    vri_score: int
    risk_grade: str
    probability_of_default: float

    executive_summary: str
    business_overview: str
    financial_analysis: str
    risk_factors: str
    strengths: str
    recommendation: str

    shap_top_factors: list[dict[str, Any]]
    model_version: str
    generated_at: str
    disclaimer: str


class GSTINListResponse(BaseModel):
    """List of available demo GSTINs."""
    gstins: list[str]
    count: int


class GSTINDetailResponse(BaseModel):
    """Detailed GSTIN data."""
    gstin: str
    legal_name: str
    trade_name: str
    state_code: str
    business_type: str
    registration_date: str
    status: str
    returns_filed_12m: int
    nil_returns_12m: int
    late_returns_12m: int
    avg_monthly_revenue: float
    revenue_trend_pct: float
    total_tax_paid_12m: float
    quarterly_revenue: list[float]
    years_in_business: float
    employee_count_est: int
    sector: str
    sub_sector: str
    litigation_flags: list[str]
    compliance_notices: int
    existing_loans: int
    total_outstanding: float
    dpd_30_count: int
    dpd_60_count: int
    dpd_90_count: int
    credit_utilization_pct: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_ready: bool
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str
    detail: str
    status_code: int
