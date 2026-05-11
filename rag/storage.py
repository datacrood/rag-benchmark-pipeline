import numpy as np


class VectorStore:
    """Simple in-memory vector index using numpy. Pre-normalizes on add so search is just a dot product."""

    def __init__(self):
        self._matrix: np.ndarray | None = None
        self._chunks: list[str] = []

    def __len__(self) -> int:
        return len(self._chunks)

    def add(self, embeddings: np.ndarray, chunks: list[str]) -> None:
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / np.where(norms == 0, 1, norms)
        if self._matrix is None:
            self._matrix = normalized
        else:
            self._matrix = np.vstack([self._matrix, normalized])
        self._chunks.extend(chunks)

    def search(self, query_vec: np.ndarray, top_k: int = 3) -> list[tuple[float, str]]:
        if self._matrix is None:
            raise ValueError("VectorStore is empty — call add() before search()")
        norm = np.linalg.norm(query_vec)
        q = query_vec / (norm if norm > 0 else 1)
        scores = self._matrix @ q
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(float(scores[i]), self._chunks[i]) for i in top_indices]
