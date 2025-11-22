"""Filter final document JSONL files by approximate token length.

Za svaki dokument koji izgleda kao:
{
  "post": {"title": ..., "text": ...},
  "comments": [{"text": ...}, ...]
}

napravi jedan veliki string (title + text + svi komentari) i ako
procena broja tokena > MAX_TOKENS (default 8000) -> taj dokument se
NE upisuje u izlaz.

Koristi grubu procenu tokena: 1 token ≈ 4 karaktera (OpenAI heuristika).
Ako kasnije hoćeš preciznije, možeš da zameniš funkciju `estimate_tokens`.
"""

from __future__ import annotations

import json
import os
import glob
from typing import Iterable

from tqdm import tqdm

MAX_TOKENS = 8000
TOKEN_CHARS_APPROX = 4  # ~4 chars per token


def estimate_tokens(text: str) -> int:
    """Vrlo gruba procena broja tokena na osnovu dužine teksta u karakterima."""

    if not text:
        return 0
    return len(text) // TOKEN_CHARS_APPROX


def iter_input_files(pattern: str) -> list[str]:
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"⚠️ Nije pronađen nijedan fajl za pattern: {pattern}")
    else:
        print(f"📂 Nađeno {len(files)} ulaznih fajlova")
    return files


def build_document_text(doc: dict) -> str:
    """Sastavi jedan veliki string: post title + post text + comment texts."""

    post = doc.get("post", {})
    title = post.get("title", "") or ""
    text = post.get("text", "") or ""

    parts = []
    if title:
        parts.append(str(title))
    if text:
        parts.append(str(text))

    comments = doc.get("comments", []) or []
    for c in comments:
        c_text = c.get("text", "") or ""
        if c_text:
            parts.append(str(c_text))

    return "\n".join(parts)


def filter_file_by_tokens(input_path: str, output_path: str, max_tokens: int = MAX_TOKENS) -> None:
    """Pročitaj jedan JSONL fajl i upiši samo dokumente <= max_tokens."""

    kept = 0
    dropped = 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as fin, open(
        output_path, "w", encoding="utf-8"
    ) as fout:
        for line in tqdm(fin, desc=os.path.basename(input_path)):
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                continue

            full_text = build_document_text(doc)
            n_tokens = estimate_tokens(full_text)

            if n_tokens > max_tokens:
                dropped += 1
                continue

            fout.write(json.dumps(doc) + "\n")
            kept += 1

    print(
        f"✅ {os.path.basename(input_path)} -> {os.path.basename(output_path)} | "
        f"zadržano: {kept}, odbačeno (preko {max_tokens} tokena): {dropped}"
    )


def batch_filter(
    input_pattern: str,
    output_dir: str,
    max_tokens: int = MAX_TOKENS,
) -> None:
    files = iter_input_files(input_pattern)
    if not files:
        return

    os.makedirs(output_dir, exist_ok=True)

    for in_path in files:
        base = os.path.basename(in_path)
        out_path = os.path.join(output_dir, base.replace(".jsonl", "_tok<=%d.jsonl" % max_tokens))
        filter_file_by_tokens(in_path, out_path, max_tokens=max_tokens)


if __name__ == "__main__":
    # Primer poziva:
    # Uzimamo dokumente koje pravi `documents.py`, npr. ./dataset/output/documents/final_docs_part_*.jsonl
    INPUT_PATTERN = "./dataset/output/documents/final_docs_part_*.jsonl"
    OUTPUT_DIR = "./dataset/output/documents_token_limited"

    batch_filter(INPUT_PATTERN, OUTPUT_DIR, max_tokens=MAX_TOKENS)
