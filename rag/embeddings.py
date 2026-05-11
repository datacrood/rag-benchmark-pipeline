import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    # wraps sentence-transformers but keeps the same interface as Vertex AI's TextEmbeddingModel
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(texts, convert_to_numpy=True).astype(np.float32)

    def encode(self, text: str) -> np.ndarray:
        return self._model.encode(text, convert_to_numpy=True).astype(np.float32)
