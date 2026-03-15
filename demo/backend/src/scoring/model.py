"""XGBoost credit scoring model — trains on synthetic data at startup.

In production this becomes a loaded model from MLflow registry.
For demo: trains a lightweight model on 5 synthetic records + augmented data.
Outputs: VRI score (0-1000) + SHAP explanations.
"""

from __future__ import annotations

import json
import math
import os
import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import xgboost as xgb

from src.core.logging import logger
from src.scoring.features import FeatureVector, extract_features
from src.scoring.repositories import GSTINData, MockGSTINRepository

# Where to cache the trained model
MODEL_DIR = Path(__file__).parent.parent.parent / "ml"
MODEL_PATH = MODEL_DIR / "demo_xgb_model.pkl"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.json"


@dataclass(frozen=True)
class ShapExplanation:
    """Single SHAP factor explaining score impact."""

    feature: str
    display_name: str
    value: float  # raw feature value
    shap_value: float  # contribution to score (positive = increases score)
    direction: str  # "positive" or "negative"
    magnitude: str  # "high", "medium", "low"


@dataclass(frozen=True)
class ScoringResult:
    """Complete scoring output — score + explanations."""

    vri_score: int  # 0-1000
    probability_of_default: float  # 0.0-1.0
    risk_grade: str  # "A+" to "D"
    shap_factors: list[ShapExplanation] = field(default_factory=list)
    feature_vector: dict[str, float] = field(default_factory=dict)
    model_version: str = "demo-v1.0"


# ── Grade thresholds ──
GRADE_THRESHOLDS = [
    (850, "A+"),
    (750, "A"),
    (650, "B+"),
    (550, "B"),
    (450, "C+"),
    (350, "C"),
    (250, "D+"),
    (0, "D"),
]

# ── Human-friendly feature names ──
FEATURE_DISPLAY_NAMES: dict[str, str] = {
    "filing_rate": "GST Filing Rate",
    "nil_return_rate": "Nil Return Frequency",
    "late_filing_rate": "Late Filing Frequency",
    "filing_consistency_score": "Filing Consistency",
    "is_active": "GST Registration Status",
    "months_since_registration": "Time Since Registration",
    "avg_monthly_revenue_log": "Monthly Revenue (scale)",
    "revenue_trend_pct": "Revenue Growth Trend",
    "revenue_volatility": "Revenue Volatility",
    "quarterly_growth_rate": "Quarterly Growth",
    "tax_to_revenue_ratio": "Tax/Revenue Ratio",
    "revenue_per_employee": "Revenue per Employee",
    "annualized_revenue_log": "Annual Revenue (scale)",
    "is_revenue_declining": "Revenue Declining Flag",
    "years_in_business": "Years in Business",
    "business_maturity_score": "Business Maturity",
    "employee_count_log": "Employee Count (scale)",
    "is_proprietorship": "Proprietorship Type",
    "is_partnership": "Partnership Type",
    "is_pvt_ltd": "Pvt Ltd Type",
    "existing_loan_count": "Existing Loans",
    "total_outstanding_log": "Total Outstanding (scale)",
    "dpd_30_count": "DPD 30+ Count",
    "dpd_60_count": "DPD 60+ Count",
    "dpd_90_count": "DPD 90+ Count",
    "credit_utilization_pct": "Credit Utilization %",
    "litigation_count": "Active Litigations",
    "compliance_notice_count": "Compliance Notices",
    "has_nclt_case": "NCLT Case Flag",
    "has_tax_notice": "Tax Notice Flag",
    "related_party_count": "Related Parties",
    "risk_flag_density": "Risk Flag Density",
    "is_suspended_or_cancelled": "Suspended/Cancelled Flag",
    "debt_to_revenue_ratio": "Debt-to-Revenue Ratio",
    "repayment_capacity_score": "Repayment Capacity",
    "overall_compliance_score": "Overall Compliance",
    "business_stability_index": "Business Stability",
    "credit_risk_composite": "Credit Risk Composite",
    "growth_momentum_score": "Growth Momentum",
    "sector_risk_premium": "Sector Risk Premium",
}


def _score_to_grade(score: int) -> str:
    """Map VRI score to letter grade."""
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "D"


def _generate_synthetic_training_data(n_samples: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """Generate augmented synthetic training data.

    Uses the 5 demo records as anchors and adds gaussian noise
    to create a realistic-looking training set.
    """
    rng = np.random.default_rng(42)  # reproducible
    repo = MockGSTINRepository()

    anchors = []
    anchor_targets = []

    # Known target probabilities of default for each demo record
    target_pd_map = {
        "27AABCM1234D1Z5": 0.05,  # Healthy → low PD
        "27XYZBN5678E2Z3": 0.65,  # Stressed → high PD
        "29PQRST9012F3Z7": 0.30,  # Borderline → medium PD
        "33ABCFP7890G4Z1": 0.12,  # Growing micro → low-medium PD
        "07DEFGH3456H5Z9": 0.85,  # Suspended → very high PD
    }

    for gstin, raw_data in repo.DEMO_GSTINS.items():
        data = GSTINData(**raw_data)
        features = extract_features(data)
        anchors.append(features.to_list())
        anchor_targets.append(target_pd_map[gstin])

    anchors_arr = np.array(anchors)  # (5, 40)
    targets_arr = np.array(anchor_targets)  # (5,)

    # Generate n_samples by sampling anchor + gaussian noise
    X_all = []
    y_all = []

    samples_per_anchor = n_samples // len(anchors)
    for i in range(len(anchors)):
        noise = rng.normal(0, 0.1, size=(samples_per_anchor, anchors_arr.shape[1]))
        perturbed = anchors_arr[i] + noise * np.abs(anchors_arr[i]) * 0.15
        X_all.append(perturbed)

        # Target PD with noise
        pd_noise = rng.normal(0, 0.08, size=samples_per_anchor)
        y_all.append(np.clip(targets_arr[i] + pd_noise, 0.01, 0.99))

    X = np.vstack(X_all).astype(np.float32)
    y = np.concatenate(y_all).astype(np.float32)

    return X, y


class CreditScoringModel:
    """XGBoost-powered credit scoring with SHAP explanations.

    Lifecycle:
    1. train_demo_model() — called once on startup
    2. score(features) — called per request

    COMPLIANCE: RBI Guidelines — Decisions must be explainable.
    SHAP values mandatory. CreditMemo.disclaimer must be present.
    """

    def __init__(self) -> None:
        self.model: xgb.XGBRegressor | None = None
        self.feature_names: list[str] = []
        self._is_ready = False

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def train_demo_model(self) -> None:
        """Train on synthetic data. ~200ms on modern hardware."""
        logger.info("Training demo XGBoost model on synthetic data...")

        X, y = _generate_synthetic_training_data(n_samples=200)

        # Extract feature names from a dummy feature vector
        repo = MockGSTINRepository()
        gstin = list(repo.DEMO_GSTINS.keys())[0]
        dummy_data = GSTINData(**repo.DEMO_GSTINS[gstin])
        dummy_features = extract_features(dummy_data)
        self.feature_names = list(dummy_features.to_dict().keys())

        self.model = xgb.XGBRegressor(
            n_estimators=50,
            max_depth=4,
            learning_rate=0.1,
            objective="reg:squarederror",
            random_state=42,
            verbosity=0,
        )
        self.model.fit(X, y)

        # Save model and feature names
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(FEATURE_NAMES_PATH, "w") as f:
            json.dump(self.feature_names, f)

        self._is_ready = True
        logger.info("Demo model trained and saved successfully. Features: %d", len(self.feature_names))

    def load_model(self) -> bool:
        """Load pre-trained model from disk if available."""
        if MODEL_PATH.exists() and FEATURE_NAMES_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(FEATURE_NAMES_PATH, "r") as f:
                self.feature_names = json.load(f)
            self._is_ready = True
            logger.info("Loaded pre-trained model from disk.")
            return True
        return False

    def score(self, features: FeatureVector) -> ScoringResult:
        """Score a single MSME. Returns VRI score + SHAP explanations.

        COMPLIANCE: RBI Guidelines — SHAP values mandatory for explainability.
        """
        if not self._is_ready or self.model is None:
            raise RuntimeError("Model not trained/loaded. Call train_demo_model() first.")

        feature_dict = features.to_dict()
        X = np.array([features.to_list()], dtype=np.float32)

        # Predict probability of default
        pd_raw = float(self.model.predict(X)[0])
        pd_clipped = max(0.01, min(0.99, pd_raw))

        # Convert PD to VRI score (0-1000, higher = better)
        vri_score = int(round((1.0 - pd_clipped) * 1000))
        vri_score = max(0, min(1000, vri_score))

        # SHAP explanations using tree-based method
        shap_factors = self._compute_shap_explanations(X, feature_dict)

        risk_grade = _score_to_grade(vri_score)

        return ScoringResult(
            vri_score=vri_score,
            probability_of_default=round(pd_clipped, 4),
            risk_grade=risk_grade,
            shap_factors=shap_factors,
            feature_vector=feature_dict,
        )

    def _compute_shap_explanations(
        self, X: np.ndarray, feature_dict: dict[str, float], top_k: int = 10
    ) -> list[ShapExplanation]:
        """Compute SHAP values and return top-k most impactful factors.

        Uses XGBoost's built-in tree SHAP (fast, exact).
        Falls back to feature importance if SHAP fails.
        """
        try:
            import shap

            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)[0]
        except Exception:
            # Fallback: use feature importance as proxy
            logger.warning("SHAP computation failed, using feature importance fallback.")
            importances = self.model.feature_importances_
            # Create pseudo-SHAP: importance * feature_value_sign
            shap_values = importances * np.sign(X[0])

        # Build explanations sorted by absolute impact
        explanations: list[ShapExplanation] = []
        indexed = list(enumerate(shap_values))
        indexed.sort(key=lambda x: abs(x[1]), reverse=True)

        for idx, sv in indexed[:top_k]:
            fname = self.feature_names[idx] if idx < len(self.feature_names) else f"feature_{idx}"
            fval = float(X[0, idx])
            abs_sv = abs(sv)

            magnitude = "high" if abs_sv > 0.1 else ("medium" if abs_sv > 0.03 else "low")

            explanations.append(
                ShapExplanation(
                    feature=fname,
                    display_name=FEATURE_DISPLAY_NAMES.get(fname, fname),
                    value=round(fval, 4),
                    shap_value=round(float(sv), 4),
                    direction="positive" if sv > 0 else "negative",
                    magnitude=magnitude,
                )
            )

        return explanations
