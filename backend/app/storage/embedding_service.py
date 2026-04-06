"""
EmbeddingService — embeddings via OpenAI-compatible API (OpenRouter, OpenAI, etc.)

Uses /embeddings endpoint compatible with OpenAI API format.
Default: openai/text-embedding-3-small via OpenRouter (1536 dimensions).
"""

import time
import logging
from typing import List, Optional

import requests

from ..config import Config

logger = logging.getLogger('jaypolymind.embedding')


class EmbeddingService:
    """Generate embeddings using OpenAI-compatible API (OpenRouter, OpenAI, etc.)."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        self.model = model or Config.EMBEDDING_MODEL
        self.base_url = (base_url or Config.EMBEDDING_BASE_URL).rstrip('/')
        self.api_key = api_key or Config.EMBEDDING_API_KEY
        self.dimensions = dimensions or Config.EMBEDDING_DIMENSIONS
        self.max_retries = max_retries
        self.timeout = timeout
        self._embed_url = f"{self.base_url}/embeddings"

        # Simple in-memory cache (text -> embedding vector)
        self._cache: dict[str, List[float]] = {}
        self._cache_max_size = 2000

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Returns:
            Float vector (length = self.dimensions)

        Raises:
            EmbeddingError: If API request fails after retries
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text")

        text = text.strip()

        if text in self._cache:
            return self._cache[text]

        vectors = self._request_embeddings([text])
        vector = vectors[0]

        self._cache_put(text, vector)
        return vector

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Processes in batches to avoid overwhelming the API.

        Returns:
            List of embedding vectors (same order as input)
        """
        if not texts:
            return []

        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for i, text in enumerate(texts):
            text = text.strip() if text else ""
            if text in self._cache:
                results[i] = self._cache[text]
            elif text:
                uncached_indices.append(i)
                uncached_texts.append(text)
            else:
                results[i] = [0.0] * self.dimensions

        if uncached_texts:
            all_vectors: List[List[float]] = []
            for start in range(0, len(uncached_texts), batch_size):
                batch = uncached_texts[start:start + batch_size]
                vectors = self._request_embeddings(batch)
                all_vectors.extend(vectors)

            for idx, vec, text in zip(uncached_indices, all_vectors, uncached_texts):
                results[idx] = vec
                self._cache_put(text, vec)

        return results  # type: ignore

    def _request_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Make HTTP request to OpenAI-compatible /embeddings endpoint with retry.

        Request format:  {"model": "...", "input": ["text1", "text2"]}
        Response format: {"data": [{"embedding": [...], "index": 0}, ...]}
        """
        payload = {
            "model": self.model,
            "input": texts,
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self._embed_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

                # OpenAI format: {"data": [{"embedding": [...], "index": N}]}
                items = data.get("data", [])
                if len(items) != len(texts):
                    raise EmbeddingError(
                        f"Expected {len(texts)} embeddings, got {len(items)}"
                    )

                # Sort by index to preserve order
                items_sorted = sorted(items, key=lambda x: x["index"])
                return [item["embedding"] for item in items_sorted]

            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(
                    f"Embedding API connection failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(
                    f"Embedding API request timed out (attempt {attempt + 1}/{self.max_retries})"
                )
            except requests.exceptions.HTTPError as e:
                last_error = e
                logger.error(f"Embedding API HTTP error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code >= 500:
                    pass  # Server error — retry
                else:
                    raise EmbeddingError(f"Embedding API error: {e}") from e
            except (KeyError, ValueError) as e:
                raise EmbeddingError(f"Invalid embedding API response: {e}") from e

            if attempt < self.max_retries - 1:
                wait = 2 ** attempt
                logger.info(f"Retrying in {wait}s...")
                time.sleep(wait)

        raise EmbeddingError(
            f"Embedding API failed after {self.max_retries} retries: {last_error}"
        )

    def _cache_put(self, text: str, vector: List[float]) -> None:
        """Add to cache, evicting oldest entries if full."""
        if len(self._cache) >= self._cache_max_size:
            keys_to_remove = list(self._cache.keys())[:self._cache_max_size // 10]
            for key in keys_to_remove:
                del self._cache[key]
        self._cache[text] = vector

    def health_check(self) -> bool:
        """Check if embedding API endpoint is reachable."""
        try:
            vec = self.embed("health check")
            return len(vec) > 0
        except Exception:
            return False


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""
    pass
