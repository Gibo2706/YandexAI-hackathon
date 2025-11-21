"""Embedding helpers (skeleton).

You will likely extend this with proper batching + FAISS index building.
"""

from __future__ import annotations

from typing import Iterable, List

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", batch_size: int = 128):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        """Encode texts into a 2D numpy array of embeddings.

        This keeps things simple for now; you can pipe to FAISS afterwards.
        """

        texts_list: List[str] = list(texts)
        if not texts_list:
            return np.zeros((0, self.model.get_sentence_embedding_dimension()), dtype="float32")

        return self.model.encode(texts_list, batch_size=self.batch_size, convert_to_numpy=True, normalize_embeddings=True)
