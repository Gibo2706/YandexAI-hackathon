# YandexAI Hackathon – Reddit Scam/Trust Embeddings

Minimal Python environment and pipeline skeleton for working with a large Reddit dump (~150 GB) to build a scam/trust retrieval system.

## 1. Python environment

Recommended: Python 3.10–3.12 on Linux.

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install .[dev]
```

If `.[dev]` fails, install the base project only:

```bash
pip install .
```

## 2. Project layout

- `dataset/` – place raw Reddit data here (JSONL, parquet, etc.). 150 GB will not be tracked in git.
- `src/` – Python package with filtering, document building, and embedding logic.
- `notebooks/` – exploratory analysis and experiments.

## 3. Intended pipeline (high-level)

Goal: You **do not** embed every single comment. Instead:

1. **Filter by topic** – keep only posts/comments that look relevant to scams/trust:
   - contain words like: `"scam"`, `"fraud"`, `"ponzi"`, `"mlm"`, `"is this a scam"`, `"legit"`, `"suspicious"`, `"lost my money"`, etc.
2. **Filter by length & quality** – ignore ultra-short stuff:
   - drop comments shorter than ~30–50 characters
   - optionally require score > 0 or > 2
3. **Build documents** instead of per-comment embeddings:
   - 1 document ≈ 1 thread or small cluster of related comments
   - e.g. root post + top-k relevant comments, or a pre-computed summary
4. **Embed & index**:
   - use a sentence-transformer to embed each document
   - store in FAISS index for retrieval

## 4. Quickstart command

Once your data is ready and env installed, you will be able to run (after we implement the pipeline):

```bash
python -m src.pipeline.run_example
```

For now this will just be a skeleton that you can extend during the hackathon.
