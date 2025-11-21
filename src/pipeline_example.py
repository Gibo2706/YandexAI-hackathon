"""Minimal example entry point; extend during hackathon.

This will eventually:
- stream raw Reddit data from `dataset/`
- filter by scam-related keywords, min length, score
- group into documents (thread-level)
- embed and store into FAISS index

For now it just prints the default config to verify the env works.
"""

from __future__ import annotations

from pprint import pprint

from .config import get_default_config


def main() -> None:
    cfg = get_default_config()
    print("Loaded config:")
    pprint(cfg.model_dump())


if __name__ == "__main__":  # pragma: no cover
    main()
