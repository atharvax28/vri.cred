"""Mock GSTIN repository — 5 synthetic MSMEs with realistic Indian business data.

Zero infrastructure cost. Swap with SurpassGSTINRepository in production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from src.core.exceptions import GSTINNotFoundError


@dataclass(frozen=True)
class GSTINData:
    """Structured GSTIN data — immutable by design.

    NOTE: Python dataclasses require all fields without defaults to come
    before fields with defaults. Keep this ordering when adding new fields.
    """

    # ── Required fields (no defaults) ──
    gstin: str
    legal_name: str
    trade_name: str
    state_code: str
    business_type: str  # "proprietorship" | "partnership" | "pvt_ltd"
    registration_date: str  # ISO date
    status: str  # "Active" | "Cancelled" | "Suspended"

    # GST Filing Data (last 12 months)
    returns_filed_12m: int  # out of 12
    nil_returns_12m: int
    late_returns_12m: int
    avg_monthly_revenue: float  # INR
    revenue_trend_pct: float  # +/- percent change YoY
    total_tax_paid_12m: float

    # Business indicators (required)
    years_in_business: float
    employee_count_est: int
    sector: str
    sub_sector: str

    # ── Optional fields (with defaults) ──

    # Quarterly revenue breakdown (last 4 quarters)
    quarterly_revenue: list[float] = field(default_factory=list)

    # Risk signals
    litigation_flags: list[str] = field(default_factory=list)
    compliance_notices: int = 0
    related_party_gstins: list[str] = field(default_factory=list)

    # Bureau-like signals (mock for demo)
    existing_loans: int = 0
    total_outstanding: float = 0.0
    dpd_30_count: int = 0  # days past due > 30
    dpd_60_count: int = 0
    dpd_90_count: int = 0
    credit_utilization_pct: float = 0.0


class GSTINRepository(Protocol):
    """Protocol — swap mock/real freely without changing callers."""

    async def fetch(self, gstin: str) -> GSTINData: ...

    async def list_available(self) -> list[str]: ...


class MockGSTINRepository:
    """Zero-cost synthetic data. Contains 5 realistic Indian MSMEs."""

    DEMO_GSTINS: dict[str, dict] = {
        # ── Healthy MSME — Manufacturing ──
        "27AABCM1234D1Z5": {
            "gstin": "27AABCM1234D1Z5",
            "legal_name": "Mehta Precision Components Pvt Ltd",
            "trade_name": "Mehta Precision",
            "state_code": "27",
            "business_type": "pvt_ltd",
            "registration_date": "2016-04-15",
            "status": "Active",
            "returns_filed_12m": 12,
            "nil_returns_12m": 0,
            "late_returns_12m": 0,
            "avg_monthly_revenue": 2850000.0,
            "revenue_trend_pct": 18.5,
            "total_tax_paid_12m": 6156000.0,
            "quarterly_revenue": [8100000, 8550000, 8900000, 8850000],
            "years_in_business": 8.5,
            "employee_count_est": 45,
            "sector": "Manufacturing",
            "sub_sector": "Auto Components",
            "litigation_flags": [],
            "compliance_notices": 0,
            "related_party_gstins": ["27AABCM1234D2Z4"],
            "existing_loans": 2,
            "total_outstanding": 4500000.0,
            "dpd_30_count": 0,
            "dpd_60_count": 0,
            "dpd_90_count": 0,
            "credit_utilization_pct": 35.0,
        },
        # ── Stressed MSME — Textile ──
        "27XYZBN5678E2Z3": {
            "gstin": "27XYZBN5678E2Z3",
            "legal_name": "Bansal Textile Traders",
            "trade_name": "Bansal Fabrics",
            "state_code": "27",
            "business_type": "proprietorship",
            "registration_date": "2019-08-22",
            "status": "Active",
            "returns_filed_12m": 7,
            "nil_returns_12m": 3,
            "late_returns_12m": 4,
            "avg_monthly_revenue": 420000.0,
            "revenue_trend_pct": -28.3,
            "total_tax_paid_12m": 756000.0,
            "quarterly_revenue": [1800000, 1400000, 900000, 940000],
            "years_in_business": 5.2,
            "employee_count_est": 8,
            "sector": "Textile",
            "sub_sector": "Fabric Trading",
            "litigation_flags": [
                "NCLT Case #2024/MH/1234 — Supplier dispute ₹12L",
                "GST Notice — Discrepancy in GSTR-2A vs GSTR-3B",
            ],
            "compliance_notices": 2,
            "related_party_gstins": [],
            "existing_loans": 3,
            "total_outstanding": 2800000.0,
            "dpd_30_count": 3,
            "dpd_60_count": 1,
            "dpd_90_count": 1,
            "credit_utilization_pct": 88.0,
        },
        # ── Borderline MSME — IT Services ──
        "29PQRST9012F3Z7": {
            "gstin": "29PQRST9012F3Z7",
            "legal_name": "Shakti Digital Solutions LLP",
            "trade_name": "Shakti Digital",
            "state_code": "29",
            "business_type": "partnership",
            "registration_date": "2020-01-10",
            "status": "Active",
            "returns_filed_12m": 10,
            "nil_returns_12m": 1,
            "late_returns_12m": 2,
            "avg_monthly_revenue": 1200000.0,
            "revenue_trend_pct": 5.2,
            "total_tax_paid_12m": 2592000.0,
            "quarterly_revenue": [3400000, 3600000, 3700000, 3700000],
            "years_in_business": 4.1,
            "employee_count_est": 22,
            "sector": "IT Services",
            "sub_sector": "Software Development",
            "litigation_flags": [],
            "compliance_notices": 1,
            "related_party_gstins": ["29PQRST9012F4Z6"],
            "existing_loans": 1,
            "total_outstanding": 1500000.0,
            "dpd_30_count": 1,
            "dpd_60_count": 0,
            "dpd_90_count": 0,
            "credit_utilization_pct": 52.0,
        },
        # ── Micro enterprise — Food Processing ──
        "33ABCFP7890G4Z1": {
            "gstin": "33ABCFP7890G4Z1",
            "legal_name": "Annapoorna Food Products",
            "trade_name": "Annapoorna Foods",
            "state_code": "33",
            "business_type": "proprietorship",
            "registration_date": "2021-06-05",
            "status": "Active",
            "returns_filed_12m": 12,
            "nil_returns_12m": 0,
            "late_returns_12m": 1,
            "avg_monthly_revenue": 680000.0,
            "revenue_trend_pct": 32.0,
            "total_tax_paid_12m": 979200.0,
            "quarterly_revenue": [1500000, 1800000, 2200000, 2640000],
            "years_in_business": 3.5,
            "employee_count_est": 12,
            "sector": "Food Processing",
            "sub_sector": "Packaged Foods",
            "litigation_flags": [],
            "compliance_notices": 0,
            "related_party_gstins": [],
            "existing_loans": 1,
            "total_outstanding": 800000.0,
            "dpd_30_count": 0,
            "dpd_60_count": 0,
            "dpd_90_count": 0,
            "credit_utilization_pct": 28.0,
        },
        # ── Recently cancelled MSME — Trading ──
        "07DEFGH3456H5Z9": {
            "gstin": "07DEFGH3456H5Z9",
            "legal_name": "Gupta & Sons General Trading",
            "trade_name": "Gupta Trading Co",
            "state_code": "07",
            "business_type": "partnership",
            "registration_date": "2017-07-01",
            "status": "Suspended",
            "returns_filed_12m": 4,
            "nil_returns_12m": 5,
            "late_returns_12m": 3,
            "avg_monthly_revenue": 180000.0,
            "revenue_trend_pct": -62.5,
            "total_tax_paid_12m": 259200.0,
            "quarterly_revenue": [900000, 600000, 300000, 360000],
            "years_in_business": 7.5,
            "employee_count_est": 4,
            "sector": "Trading",
            "sub_sector": "General Merchandise",
            "litigation_flags": [
                "Income Tax Notice — AY 2023-24 demand ₹4.2L",
                "NCLT Case #2023/DL/5678 — Creditor petition",
                "Consumer Forum complaint #CF/2024/891",
            ],
            "compliance_notices": 4,
            "related_party_gstins": ["07DEFGH3456H6Z8"],
            "existing_loans": 4,
            "total_outstanding": 6200000.0,
            "dpd_30_count": 4,
            "dpd_60_count": 3,
            "dpd_90_count": 2,
            "credit_utilization_pct": 95.0,
        },
    }

    async def fetch(self, gstin: str) -> GSTINData:
        """Fetch synthetic GSTIN data. Raises GSTINNotFoundError if not found."""
        raw = self.DEMO_GSTINS.get(gstin.upper())
        if raw is None:
            raise GSTINNotFoundError(gstin)
        return GSTINData(**raw)

    async def list_available(self) -> list[str]:
        """Return all demo GSTINs available for testing."""
        return list(self.DEMO_GSTINS.keys())
