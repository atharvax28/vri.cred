"""Full scoring pipeline — orchestrates: GSTIN fetch → feature extraction → model score."""

from __future__ import annotations

from src.core.logging import logger
from src.core.utils import mask_gstin
from src.scoring.features import extract_features
from src.scoring.model import CreditScoringModel, ScoringResult
from src.scoring.repositories import GSTINData, GSTINRepository


async def run_scoring_pipeline(
    gstin: str,
    repository: GSTINRepository,
    model: CreditScoringModel,
) -> tuple[ScoringResult, GSTINData]:
    """Full end-to-end scoring.

    Returns (ScoringResult, GSTINData) tuple — caller needs both for report generation.
    """
    logger.info("Starting scoring pipeline for %s", mask_gstin(gstin))

    # Step 1: Fetch GSTIN data
    data = await repository.fetch(gstin)
    logger.info("Fetched GSTIN data: %s — %s", data.trade_name, data.status)

    # Step 2: Extract features
    features = extract_features(data)
    logger.info("Extracted %d features", features.final_feature_count)

    # Step 3: Score
    result = model.score(features)
    logger.info(
        "Scoring complete — VRI: %d (%s), PD: %.2f%%",
        result.vri_score,
        result.risk_grade,
        result.probability_of_default * 100,
    )

    return result, data
