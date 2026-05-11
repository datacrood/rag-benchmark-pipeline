import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from rag.embeddings import EmbeddingModel
from rag.storage import VectorStore
from rag.retrieval import QueryExpander, RAGEngine


SAMPLE_CHUNKS = [
    "Auto-scaling adjusts compute capacity in response to traffic demand.",
    "Heartbeat monitoring detects node failures and triggers automatic failover.",
    "TLS 1.3 encrypts all data in transit using forward secrecy.",
    "VPC subnets isolate public and private network tiers.",
    "Kubernetes HPA scales pod replicas based on CPU and memory metrics.",
]


@pytest.fixture(scope="session")
def engine():
    """Pre-ingested RAGEngine with 5 real corpus chunks. Uses real sentence-transformers."""
    em = EmbeddingModel()
    store = VectorStore()
    expander = QueryExpander()
    eng = RAGEngine(em, store, expander)
    eng.ingest(SAMPLE_CHUNKS)
    return eng


@pytest.fixture
def mock_vertex_embedding():
    """Patches the vertexai TextEmbeddingModel import target."""
    with patch("rag.embeddings.SentenceTransformer") as mock:
        mock_instance = MagicMock()
        mock_instance.encode.return_value = np.random.rand(384).astype(np.float32)
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_vertex_generative():
    """Patches vertexai GenerativeModel (placeholder for production swap)."""
    with patch("rag.retrieval.EXPANSION_MAP", {}):
        yield
