import numpy as np
import pytest
from unittest.mock import MagicMock, patch


def test_get_embeddings_returns_2d_array():
    with patch("rag.embeddings.SentenceTransformer") as MockST:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(3, 384).astype(np.float32)
        MockST.return_value = mock_model

        from rag.embeddings import EmbeddingModel
        em = EmbeddingModel()
        result = em.get_embeddings(["a", "b", "c"])

        assert isinstance(result, np.ndarray)
        assert result.shape == (3, 384)
        assert result.dtype == np.float32


def test_get_embeddings_single_text_returns_2d():
    with patch("rag.embeddings.SentenceTransformer") as MockST:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(1, 384).astype(np.float32)
        MockST.return_value = mock_model

        from rag.embeddings import EmbeddingModel
        em = EmbeddingModel()
        result = em.get_embeddings(["single text"])

        assert result.shape == (1, 384)


def test_encode_returns_1d_array():
    with patch("rag.embeddings.SentenceTransformer") as MockST:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        MockST.return_value = mock_model

        from rag.embeddings import EmbeddingModel
        em = EmbeddingModel()
        result = em.encode("hello world")

        assert isinstance(result, np.ndarray)
        assert result.shape == (384,)


def test_custom_model_name_passed_to_sentence_transformer():
    with patch("rag.embeddings.SentenceTransformer") as MockST:
        MockST.return_value = MagicMock()
        MockST.return_value.encode.return_value = np.zeros((1, 384), dtype=np.float32)

        from rag.embeddings import EmbeddingModel
        EmbeddingModel(model_name="custom-model")

        MockST.assert_called_once_with("custom-model")
