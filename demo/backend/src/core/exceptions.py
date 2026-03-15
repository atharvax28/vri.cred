"""Custom exception hierarchy — never expose internal details to clients."""

from __future__ import annotations


class AppError(Exception):
    """Base app error — all custom exceptions inherit from this."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GSTINNotFoundError(AppError):
    """Raised when a GSTIN is not found in the repository."""

    def __init__(self, gstin: str) -> None:
        super().__init__(
            message=f"GSTIN {gstin} not found in the system",
            status_code=404,
        )


class GSTINValidationError(AppError):
    """Raised when GSTIN format is invalid."""

    def __init__(self, gstin: str) -> None:
        super().__init__(
            message=f"Invalid GSTIN format: {gstin}",
            status_code=422,
        )


class ScoringError(AppError):
    """Raised when the scoring pipeline fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message=f"Scoring failed: {detail}",
            status_code=500,
        )


class ReportGenerationError(AppError):
    """Raised when Claude API report generation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message=f"Report generation failed: {detail}",
            status_code=500,
        )


class JobNotFoundError(AppError):
    """Raised when a job_id doesn't exist in the queue."""

    def __init__(self, job_id: str) -> None:
        super().__init__(
            message=f"Job {job_id} not found",
            status_code=404,
        )
