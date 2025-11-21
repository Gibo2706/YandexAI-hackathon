"""Document building from Reddit records.

Goal: move from comment-level to document-level units (thread, cluster, etc.).
This is just a placeholder; adapt once you know your exact schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .filtering import RedditRecord


@dataclass
class Document:
    id: str
    text: str


def build_naive_documents(records: Iterable[RedditRecord], *, max_chars: int = 3000) -> List[Document]:
    """Very naive document builder: just chunks stream into blobs of ~max_chars.

    Later you can group by thread ID instead.
    """

    docs: List[Document] = []
    current_parts: List[str] = []
    current_len = 0
    idx = 0

    for r in records:
        t = r.text.strip()
        if not t:
            continue
        if current_len + len(t) > max_chars and current_parts:
            docs.append(Document(id=f"chunk-{idx}", text="\n".join(current_parts)))
            idx += 1
            current_parts = []
            current_len = 0

        current_parts.append(t)
        current_len += len(t)

    if current_parts:
        docs.append(Document(id=f"chunk-{idx}", text="\n".join(current_parts)))

    return docs
