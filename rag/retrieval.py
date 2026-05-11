from rag.embeddings import EmbeddingModel
from rag.storage import VectorStore

EXPANSION_MAP: dict[str, str] = {
    "peak load": (
        "peak load traffic spike high concurrency auto-scaling load balancer burst capacity "
        "horizontal scaling throughput"
    ),
    "node fail": (
        "node failure cluster recovery heartbeat leader election replica failover "
        "availability zone pod restart"
    ),
    "data secur": (
        "data security TLS mTLS encryption in transit certificate PKI forward secrecy "
        "mutual authentication"
    ),
    "latency": (
        "latency RTT round-trip packet delay bandwidth throughput jitter network performance "
        "p99 tail latency"
    ),
    "autoscal": (
        "auto-scaling horizontal scaling vertical scaling pod scaling HPA Kubernetes "
        "resource limits capacity"
    ),
    "replicat": (
        "replication WAL primary replica synchronous asynchronous failover consistency "
        "database standby"
    ),
    "observ": (
        "observability metrics logs traces OpenTelemetry Prometheus latency histogram "
        "error rate span context"
    ),
}

FALLBACK = "scalability reliability availability performance fault tolerance distributed systems"


class QueryExpander:
    # mocks GenerativeModel — swap expand() body for a real LLM call in prod
    def expand(self, query: str) -> str:
        query_lower = query.lower()
        for key, expansion in EXPANSION_MAP.items():
            if key in query_lower:
                return f"{query} {expansion}"
        return f"{query} {FALLBACK}"


class RAGEngine:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        store: VectorStore,
        expander: QueryExpander,
    ):
        self.embedding_model = embedding_model
        self.store = store
        self.expander = expander

    def ingest(self, chunks: list[str]) -> None:
        embeddings = self.embedding_model.get_embeddings(chunks)
        self.store.add(embeddings, chunks)

    def retrieve(self, query: str, strategy: str = "A", top_k: int = 3) -> dict:
        if strategy == "A":
            vec = self.embedding_model.encode(query)
            results = self.store.search(vec, top_k)
            return {"query": query, "strategy": "A", "results": results}
        elif strategy == "B":
            expanded = self.expander.expand(query)
            vec = self.embedding_model.encode(expanded)
            results = self.store.search(vec, top_k)
            return {
                "query": query,
                "expanded_query": expanded,
                "strategy": "B",
                "results": results,
            }
        else:
            raise ValueError(f"Unknown strategy '{strategy}'. Use 'A' or 'B'.")
