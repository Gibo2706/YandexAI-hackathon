"""Very small smoke test to check that the env + basic modules import correctly."""

from src.config import get_default_config
from src.filtering import RedditRecord, is_relevant
from src.documents import build_naive_documents


def test_basic_flow():
    cfg = get_default_config()

    recs = [
        RedditRecord(text="This is a scam, lost my money", score=5),
        RedditRecord(text="lol", score=10),
    ]

    filtered = list(
        r
        for r in recs
        if is_relevant(
            r,
            min_chars=cfg.filters.min_chars,
            min_score=cfg.filters.min_score,
            scam_keywords=cfg.filters.scam_keywords,
        )
    )

    assert len(filtered) == 1

    docs = build_naive_documents(filtered, max_chars=1000)
    assert len(docs) == 1
    assert "scam" in docs[0].text.lower()
