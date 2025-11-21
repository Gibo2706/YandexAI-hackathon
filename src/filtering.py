"""Filtering utilities for massive Reddit dump.

This is intentionally light so you can adapt it to your exact schema.
Assumes each record is a dict with fields like:
- body or selftext
- score
- title (for posts)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class RedditRecord:
    text: str
    score: int | None = None


def is_relevant(record: RedditRecord, min_chars: int, min_score: int, scam_keywords: list[str]) -> bool:
    text = (record.text or "").lower()
    if len(text) < min_chars:
        return False

    if record.score is not None and record.score < min_score:
        return False

    return any(kw in text for kw in scam_keywords)


def filter_stream(
    records: Iterable[RedditRecord],
    *,
    min_chars: int,
    min_score: int,
    scam_keywords: list[str],
) -> Iterable[RedditRecord]:
    """Yield only relevant records (lazy, streaming friendly)."""

    for r in records:
        if is_relevant(r, min_chars=min_chars, min_score=min_score, scam_keywords=scam_keywords):
            yield r
