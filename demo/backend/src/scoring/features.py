"""Feature extraction — converts raw GSTIN data into a numeric feature vector.

40+ features across 6 categories:
1. Filing Compliance (6 features)
2. Revenue & Growth (8 features)
3. Business Profile (5 features)
4. Credit History (6 features)
5. Risk Signals (7 features)
6. Derived / Composite (8+ features)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.scoring.repositories import GSTINData


@dataclass(frozen=True)
class FeatureVector:
    """Typed feature container — immutable, with all 40+ features as named fields."""

    # ── Filing Compliance ──
    filing_rate: float  # returns_filed / 12
    nil_return_rate: float  # nil_returns / 12
    late_filing_rate: float  # late_returns / 12
    filing_consistency_score: float  # composite 0-1
    is_active: float  # 1 if Active else 0
    months_since_registration: float

    # ── Revenue & Growth ──
    avg_monthly_revenue_log: float  # log10(avg_monthly + 1)
    revenue_trend_pct: float
    revenue_volatility: float  # std(quarterly) / mean(quarterly)
    quarterly_growth_rate: float  # Q4/Q1 - 1
    tax_to_revenue_ratio: float
    revenue_per_employee: float
    annualized_revenue_log: float
    is_revenue_declining: float  # 1 if trend < -10%

    # ── Business Profile ──
    years_in_business: float
    business_maturity_score: float  # sigmoid(years_in_business - 3)
    employee_count_log: float  # log2(employees + 1)
    is_proprietorship: float
    is_partnership: float
    is_pvt_ltd: float

    # ── Credit History ──
    existing_loan_count: float
    total_outstanding_log: float
    dpd_30_count: float
    dpd_60_count: float
    dpd_90_count: float
    credit_utilization_pct: float

    # ── Risk Signals ──
    litigation_count: float
    compliance_notice_count: float
    has_nclt_case: float  # 1 if any litigation contains "NCLT"
    has_tax_notice: float  # 1 if any litigation contains "Tax Notice"
    related_party_count: float
    risk_flag_density: float  # (litigation + notices) / years_in_business
    is_suspended_or_cancelled: float

    # ── Derived / Composite ──
    debt_to_revenue_ratio: float  # outstanding / (avg_monthly * 12)
    repayment_capacity_score: float  # composite
    overall_compliance_score: float  # weighted mix of filing + compliance
    business_stability_index: float  # composite of maturity + revenue stability
    credit_risk_composite: float  # weighted DPD + utilization
    growth_momentum_score: float  # trend + quarterly accel
    sector_risk_premium: float  # sector-based adjustment
    final_feature_count: int = 40  # metadata

    def to_dict(self) -> dict[str, float]:
        """Convert to dict for model input — excludes metadata fields."""
        d = {k: v for k, v in self.__dict__.items() if k != "final_feature_count"}
        return d

    def to_list(self) -> list[float]:
        """Ordered float vector for model input."""
        return list(self.to_dict().values())


# ── Sector risk premiums (higher = riskier) ──
SECTOR_RISK_MAP: dict[str, float] = {
    "Manufacturing": 0.15,
    "IT Services": 0.10,
    "Food Processing": 0.20,
    "Textile": 0.30,
    "Trading": 0.35,
    "Construction": 0.40,
    "Healthcare": 0.12,
    "Education": 0.18,
}


def _sigmoid(x: float) -> float:
    """Standard sigmoid function — maps any real to (0, 1)."""
    return 1.0 / (1.0 + math.exp(-x))


def _safe_log(val: float, base: float = 10.0) -> float:
    """Log with floor to avoid log(0)."""
    return math.log(max(val, 1.0)) / math.log(base)


def _revenue_volatility(quarterly: list[float]) -> float:
    """Coefficient of variation of quarterly revenue."""
    if not quarterly or len(quarterly) < 2:
        return 0.0
    mean_q = sum(quarterly) / len(quarterly)
    if mean_q == 0:
        return 1.0
    variance = sum((q - mean_q) ** 2 for q in quarterly) / len(quarterly)
    return math.sqrt(variance) / mean_q


def extract_features(data: GSTINData) -> FeatureVector:
    """Extract 40+ numeric features from raw GSTIN data.

    All features are numeric (float) — ready for XGBoost consumption.
    """
    # ── Filing Compliance ──
    filing_rate = data.returns_filed_12m / 12.0
    nil_return_rate = data.nil_returns_12m / 12.0
    late_filing_rate = data.late_returns_12m / 12.0
    filing_consistency = filing_rate * (1 - nil_return_rate) * (1 - late_filing_rate * 0.5)
    is_active = 1.0 if data.status == "Active" else 0.0

    # Approximate months since registration
    # (simplified — in production use proper date math)
    months_since_reg = data.years_in_business * 12

    # ── Revenue & Growth ──
    avg_rev_log = _safe_log(data.avg_monthly_revenue + 1)
    rev_vol = _revenue_volatility(data.quarterly_revenue)

    q_rev = data.quarterly_revenue
    quarterly_growth = (q_rev[-1] / q_rev[0] - 1.0) if q_rev and q_rev[0] > 0 else 0.0

    annual_revenue = data.avg_monthly_revenue * 12
    tax_ratio = data.total_tax_paid_12m / max(annual_revenue, 1.0)
    rev_per_emp = data.avg_monthly_revenue / max(data.employee_count_est, 1)
    ann_rev_log = _safe_log(annual_revenue + 1)
    is_declining = 1.0 if data.revenue_trend_pct < -10.0 else 0.0

    # ── Business Profile ──
    maturity = _sigmoid(data.years_in_business - 3.0)
    emp_log = _safe_log(data.employee_count_est + 1, base=2.0)
    is_prop = 1.0 if data.business_type == "proprietorship" else 0.0
    is_part = 1.0 if data.business_type == "partnership" else 0.0
    is_pvt = 1.0 if data.business_type == "pvt_ltd" else 0.0

    # ── Credit History ──
    outstanding_log = _safe_log(data.total_outstanding + 1)

    # ── Risk Signals ──
    lit_count = float(len(data.litigation_flags))
    has_nclt = 1.0 if any("nclt" in f.lower() for f in data.litigation_flags) else 0.0
    has_tax = 1.0 if any("tax notice" in f.lower() or "income tax" in f.lower() for f in data.litigation_flags) else 0.0
    related_count = float(len(data.related_party_gstins))
    risk_density = (lit_count + data.compliance_notices) / max(data.years_in_business, 0.5)
    is_suspended = 1.0 if data.status in ("Suspended", "Cancelled") else 0.0

    # ── Derived / Composite ──
    debt_to_rev = data.total_outstanding / max(annual_revenue, 1.0)

    # Repayment capacity: higher revenue + lower debt + fewer DPDs = better
    repayment_raw = (avg_rev_log * 0.4 - outstanding_log * 0.3
                     - data.dpd_90_count * 0.2 - data.credit_utilization_pct / 100 * 0.1)
    repayment_score = _sigmoid(repayment_raw)

    # Compliance composite
    compliance_score = filing_consistency * 0.6 + (1.0 - min(data.compliance_notices, 5) / 5.0) * 0.4

    # Business stability
    stability = maturity * 0.4 + (1.0 - rev_vol) * 0.3 + filing_rate * 0.3

    # Credit risk composite — higher = riskier
    credit_risk = (
        data.dpd_30_count * 0.15
        + data.dpd_60_count * 0.25
        + data.dpd_90_count * 0.40
        + data.credit_utilization_pct / 100 * 0.20
    )

    # Growth momentum
    growth_momentum = _sigmoid(data.revenue_trend_pct / 20 + quarterly_growth)

    # Sector risk
    sector_risk = SECTOR_RISK_MAP.get(data.sector, 0.25)

    return FeatureVector(
        filing_rate=filing_rate,
        nil_return_rate=nil_return_rate,
        late_filing_rate=late_filing_rate,
        filing_consistency_score=filing_consistency,
        is_active=is_active,
        months_since_registration=months_since_reg,
        avg_monthly_revenue_log=avg_rev_log,
        revenue_trend_pct=data.revenue_trend_pct,
        revenue_volatility=rev_vol,
        quarterly_growth_rate=quarterly_growth,
        tax_to_revenue_ratio=tax_ratio,
        revenue_per_employee=rev_per_emp,
        annualized_revenue_log=ann_rev_log,
        is_revenue_declining=is_declining,
        years_in_business=data.years_in_business,
        business_maturity_score=maturity,
        employee_count_log=emp_log,
        is_proprietorship=is_prop,
        is_partnership=is_part,
        is_pvt_ltd=is_pvt,
        existing_loan_count=float(data.existing_loans),
        total_outstanding_log=outstanding_log,
        dpd_30_count=float(data.dpd_30_count),
        dpd_60_count=float(data.dpd_60_count),
        dpd_90_count=float(data.dpd_90_count),
        credit_utilization_pct=data.credit_utilization_pct,
        litigation_count=lit_count,
        compliance_notice_count=float(data.compliance_notices),
        has_nclt_case=has_nclt,
        has_tax_notice=has_tax,
        related_party_count=related_count,
        risk_flag_density=risk_density,
        is_suspended_or_cancelled=is_suspended,
        debt_to_revenue_ratio=debt_to_rev,
        repayment_capacity_score=repayment_score,
        overall_compliance_score=compliance_score,
        business_stability_index=stability,
        credit_risk_composite=credit_risk,
        growth_momentum_score=growth_momentum,
        sector_risk_premium=sector_risk,
    )
