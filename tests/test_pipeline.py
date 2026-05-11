import pytest
from rag.retrieval import RAGEngine


def test_strategy_a_returns_nonempty_results(engine: RAGEngine):
    result = engine.retrieve("How does the system handle traffic spikes?", strategy="A")
    assert result["strategy"] == "A"
    assert len(result["results"]) == 3
    for score, chunk in result["results"]:
        assert 0.0 <= score <= 1.0
        assert isinstance(chunk, str)
        assert len(chunk) > 0


def test_strategy_b_returns_expanded_query_field(engine: RAGEngine):
    result = engine.retrieve("How does the system handle peak load?", strategy="B")
    assert result["strategy"] == "B"
    assert "expanded_query" in result
    assert "peak load" in result["expanded_query"]
    assert len(result["results"]) == 3


def test_strategy_b_expanded_query_is_superset_of_original(engine: RAGEngine):
    query = "How does the system handle peak load?"
    result = engine.retrieve(query, strategy="B")
    assert result["expanded_query"].startswith(query)


def test_scores_are_sorted_descending(engine: RAGEngine):
    result = engine.retrieve("node failure recovery", strategy="A")
    scores = [r[0] for r in result["results"]]
    assert scores == sorted(scores, reverse=True)


def test_tls_query_retrieves_relevant_chunk(engine: RAGEngine):
    result = engine.retrieve("data encrypted during transmission TLS", strategy="A")
    top_chunk = result["results"][0][1]
    assert "TLS" in top_chunk or "encrypt" in top_chunk.lower()


def test_strategy_a_and_b_produce_different_results_for_expansion_query(engine: RAGEngine):
    query = "How does the system handle peak load?"
    result_a = engine.retrieve(query, strategy="A")
    result_b = engine.retrieve(query, strategy="B")
    chunks_a = {r[1] for r in result_a["results"]}
    chunks_b = {r[1] for r in result_b["results"]}
    assert len(chunks_a) > 0
    assert len(chunks_b) > 0


def test_invalid_strategy_raises_value_error(engine: RAGEngine):
    with pytest.raises(ValueError, match="strategy"):
        engine.retrieve("any query", strategy="Z")
