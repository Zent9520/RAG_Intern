"""Small adapter for a future BGE embedding deployment.

Set the BGE_* environment values when the embedding endpoint is available.
The adapter supports the two most common endpoint contracts:

* ``openai``: ``POST {endpoint}`` with ``{"model": ..., "input": ...}``
  and response ``{"data": [{"embedding": [...]}]}``.
* ``huggingface``: ``POST {endpoint}`` with ``{"inputs": ...}`` and response
  ``[[...]]`` (or ``{"embedding": [...]}``).

If the eventual BGE service uses another contract, only this adapter needs to
be updated; legal-review retrieval remains unchanged.
"""

from __future__ import annotations

import math
from typing import Any

import httpx

from app.core.settings import settings


class BGEEmbeddingService:
    """Create query embeddings in the same BGE vector space as the legal index."""

    DEFAULT_TIMEOUT_SECONDS = 30.0

    def __init__(self) -> None:
        self.endpoint = (settings.BGE_EMBEDDING_ENDPOINT or "").strip()
        self.api_key = (settings.BGE_EMBEDDING_API_KEY or "").strip()
        self.model = (settings.BGE_EMBEDDING_MODEL or "BAAI/bge-m3").strip()
        self.request_format = (
            settings.BGE_EMBEDDING_REQUEST_FORMAT or "openai"
        ).strip().lower()
        self.query_prefix = settings.BGE_QUERY_PREFIX or ""

    def embed(self, text: str) -> list[float]:
        """Return one BGE embedding for a retrieval query.

        The prefix is intentionally configurable.  It must match the query
        instruction, if any, used while building the legal Azure Index.
        """

        if not self.endpoint:
            raise RuntimeError(
                "BGE_EMBEDDING_ENDPOINT is not configured. Configure the BGE "
                "deployment before calling legal vector retrieval."
            )
        if not text or not text.strip():
            raise ValueError("BGE embedding input must not be empty.")

        request_text = f"{self.query_prefix}{text.strip()}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = self._build_payload(request_text)
        with httpx.Client(timeout=self.DEFAULT_TIMEOUT_SECONDS) as client:
            response = client.post(
                self.endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        vector = self._extract_vector(response.json())
        if settings.BGE_NORMALIZE_EMBEDDINGS:
            vector = self._normalize(vector)
        return vector

    def _build_payload(self, text: str) -> dict[str, Any]:
        if self.request_format == "openai":
            return {"model": self.model, "input": text}
        if self.request_format == "huggingface":
            return {"inputs": text}
        raise ValueError(
            "BGE_EMBEDDING_REQUEST_FORMAT must be 'openai' or 'huggingface'."
        )

    @staticmethod
    def _extract_vector(payload: Any) -> list[float]:
        candidate: Any = None

        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                candidate = data[0].get("embedding")
            if candidate is None:
                candidate = payload.get("embedding")
            if candidate is None:
                embeddings = payload.get("embeddings")
                if isinstance(embeddings, list) and embeddings:
                    candidate = embeddings[0]
        elif isinstance(payload, list) and payload:
            candidate = payload[0]

        # Hugging Face feature-extraction endpoints may return [[float, ...]].
        if isinstance(candidate, list) and candidate and isinstance(candidate[0], list):
            candidate = candidate[0]

        if not isinstance(candidate, list) or not all(
            isinstance(value, int | float) for value in candidate
        ):
            raise RuntimeError(
                "BGE endpoint response does not contain an embedding vector. "
                "Update BGEEmbeddingService._extract_vector for its response schema."
            )

        return [float(value) for value in candidate]

    @staticmethod
    def _normalize(vector: list[float]) -> list[float]:
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            raise RuntimeError("BGE endpoint returned a zero embedding vector.")
        return [value / magnitude for value in vector]
