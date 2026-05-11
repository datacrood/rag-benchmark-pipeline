import numpy as np
import pytest
from rag.storage import VectorStore


def test_cosine_identical_vectors_score_is_one():
    store = VectorStore()
    vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    store.add(vec.reshape(1, -1), ["identical chunk"])
    results = store.search(vec, top_k=1)
    assert len(results) == 1
    score, chunk = results[0]
    assert abs(score - 1.0) < 1e-5
    assert chunk == "identical chunk"


def test_cosine_orthogonal_vectors_score_is_zero():
    store = VectorStore()
    vec_a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    vec_b = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    store.add(vec_a.reshape(1, -1), ["chunk a"])
    results = store.search(vec_b, top_k=1)
    score, _ = results[0]
    assert abs(score) < 1e-5


def test_search_returns_top_k_sorted_descending():
    store = VectorStore()
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    embeddings = np.array([
        [0.99, 0.14, 0.0],   # high sim
        [0.0,  1.0,  0.0],   # low sim (orthogonal)
        [0.71, 0.71, 0.0],   # medium sim
    ], dtype=np.float32)
    store.add(embeddings, ["high", "low", "medium"])
    results = store.search(query, top_k=3)
    assert len(results) == 3
    scores = [r[0] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0][1] == "high"


def test_search_top_k_truncates():
    store = VectorStore()
    embeddings = np.eye(5, dtype=np.float32)
    store.add(embeddings, [f"chunk {i}" for i in range(5)])
    query = np.array([1.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    results = store.search(query, top_k=2)
    assert len(results) == 2


def test_search_empty_store_raises():
    store = VectorStore()
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    with pytest.raises(ValueError, match="empty"):
        store.search(query)


def test_add_multiple_batches_accumulates():
    store = VectorStore()
    batch1 = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    batch2 = np.array([[0.707, 0.707]], dtype=np.float32)
    store.add(batch1, ["a", "b"])
    store.add(batch2, ["c"])
    assert len(store) == 3
