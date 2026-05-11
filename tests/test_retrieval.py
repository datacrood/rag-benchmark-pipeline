import numpy as np
import pytest
from unittest.mock import MagicMock, patch, call
from rag.retrieval import QueryExpander, RAGEngine
from rag.embeddings import EmbeddingModel
from rag.storage import VectorStore


# --- QueryExpander tests ---

def test_expander_peak_load_query():
    expander = QueryExpander()
    result = expander.expand("How does the system handle peak load?")
    assert "peak load" in result
    assert "auto-scaling" in result or "traffic spike" in result


def test_expander_node_failure_query():
    expander = QueryExpander()
    result = expander.expand("What happens when a node fails in the cluster?")
    assert "failover" in result or "heartbeat" in result


def test_expander_data_security_query():
    expander = QueryExpander()
    result = expander.expand("How is data secured during transmission?")
    assert "TLS" in result or "encryption" in result


def test_expander_unknown_query_appends_fallback():
    expander = QueryExpander()
    result = expander.expand("What is the color of the sky?")
    assert "What is the color of the sky?" in result
    assert "scalability" in result or "reliability" in result


def test_expander_original_query_preserved_in_expansion():
    expander = QueryExpander()
    original = "How does the system handle peak load?"
    result = expander.expand(original)
    assert result.startswith(original)


# --- RAGEngine tests ---

def _make_engine():
    mock_em = MagicMock(spec=EmbeddingModel)
    mock_em.encode.return_value = np.random.rand(384).astype(np.float32)
    mock_em.get_embeddings.return_value = np.random.rand(3, 384).astype(np.float32)
    mock_store = MagicMock(spec=VectorStore)
    mock_store.search.return_value = [(0.9, "chunk a"), (0.8, "chunk b"), (0.7, "chunk c")]
    mock_expander = MagicMock(spec=QueryExpander)
    mock_expander.expand.return_value = "expanded query text"
    return RAGEngine(mock_em, mock_store, mock_expander), mock_em, mock_store, mock_expander


def test_strategy_a_does_not_call_expander():
    engine, mock_em, mock_store, mock_expander = _make_engine()
    result = engine.retrieve("test query", strategy="A")
    mock_expander.expand.assert_not_called()
    assert result["strategy"] == "A"
    assert result["query"] == "test query"
    assert len(result["results"]) == 3


def test_strategy_b_calls_expander_and_uses_expanded_query():
    engine, mock_em, mock_store, mock_expander = _make_engine()
    result = engine.retrieve("test query", strategy="B")
    mock_expander.expand.assert_called_once_with("test query")
    mock_em.encode.assert_called_once_with("expanded query text")
    assert result["strategy"] == "B"
    assert result["expanded_query"] == "expanded query text"
    assert len(result["results"]) == 3


def test_strategy_a_calls_encode_with_original_query():
    engine, mock_em, mock_store, mock_expander = _make_engine()
    engine.retrieve("my query", strategy="A")
    mock_em.encode.assert_called_once_with("my query")


def test_ingest_calls_get_embeddings_and_store_add():
    engine, mock_em, mock_store, mock_expander = _make_engine()
    chunks = ["chunk 1", "chunk 2", "chunk 3"]
    engine.ingest(chunks)
    mock_em.get_embeddings.assert_called_once_with(chunks)
    mock_store.add.assert_called_once()


def test_invalid_strategy_raises():
    engine, _, _, _ = _make_engine()
    with pytest.raises(ValueError, match="strategy"):
        engine.retrieve("query", strategy="C")
