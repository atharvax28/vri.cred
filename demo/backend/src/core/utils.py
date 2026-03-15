"""Utility functions — sanitization, formatting, helpers."""

from __future__ import annotations

import html
import re


def sanitize_for_llm_context(raw_text: str, max_length: int = 2000) -> str:
    """Strip injection attempts. Call on ALL external data before LLM context.

    SECURITY: Blocks known prompt injection patterns and escapes HTML entities.
    """
    for pattern in [
        r"ignore previous instructions",
        r"disregard.*instructions",
        r"you are now",
        r"system:",
        r"<\|.*\|>",
        r"\[INST\]",
        r"</s>",
        r"<<SYS>>",
    ]:
        raw_text = re.sub(pattern, "[REDACTED]", raw_text, flags=re.IGNORECASE)

    return html.escape(raw_text)[:max_length]


def format_currency_inr(amount: float) -> str:
    """Format amount in Indian Rupee notation (e.g., 12,34,567.89)."""
    if amount < 0:
        return f"-₹{format_currency_inr(abs(amount))[1:]}"

    integer_part = int(amount)
    decimal_part = f"{amount - integer_part:.2f}"[1:]  # .XX

    s = str(integer_part)
    if len(s) <= 3:
        return f"₹{s}{decimal_part}"

    # Indian grouping: last 3 digits, then groups of 2
    last_three = s[-3:]
    remaining = s[:-3]
    groups = []
    while remaining:
        groups.append(remaining[-2:])
        remaining = remaining[:-2]
    groups.reverse()

    return f"₹{','.join(groups)},{last_three}{decimal_part}"


def mask_gstin(gstin: str) -> str:
    """Mask middle characters of GSTIN for logging — never log full GSTIN."""
    if len(gstin) != 15:
        return "INVALID"
    return f"{gstin[:4]}{'*' * 7}{gstin[-4:]}"
