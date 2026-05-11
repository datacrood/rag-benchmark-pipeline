# RAG Pipeline

Local RAG pipeline built for the Senior Gen AI Assessment. Compares two retrieval strategies over a cloud infrastructure document corpus.

## Setup

```bash
pip install -r requirements.txt
pytest tests/ -v
python -m rag.benchmark
```

## Structure

```
rag_pipeline/
├── data/corpus.py          # 10 cloud infra paragraphs used as the document store
├── rag/
│   ├── embeddings.py       # EmbeddingModel wrapping sentence-transformers
│   ├── storage.py          # VectorStore — numpy cosine similarity index
│   ├── retrieval.py        # QueryExpander + RAGEngine
│   └── benchmark.py        # runs Strategy A vs B, writes retrieval_benchmark.md
└── tests/                  # unit + integration tests (27 total)
```

## Similarity Metric: Cosine vs Euclidean

I went with cosine similarity. The core reason: text embeddings encode meaning as direction, not magnitude. A 3-sentence and a 10-sentence paragraph on the same topic point roughly the same direction in embedding space but have very different vector lengths. Cosine ignores that length difference:

```
cosine_sim(A, B) = (A · B) / (|A| × |B|)
```

Euclidean distance would penalize the longer paragraph just for being longer, even if it's semantically identical. That's not what we want here.

The implementation pre-normalizes all vectors on ingest (L2 norm = 1), so at query time cosine similarity collapses to a plain dot product — no division, just a matrix multiply.

Euclidean makes more sense when magnitude is meaningful, like image pixel vectors or geographic distances. For transformer sentence embeddings: cosine.

---

## Migrating to Vertex AI

The classes are designed so each one can be swapped independently — `RAGEngine` doesn't need to change at all.

### Step 1: Swap EmbeddingModel

Replace `SentenceTransformer` with `TextEmbeddingModel.from_pretrained("textembedding-gecko@003")`. The method signatures stay the same, so nothing else changes. `gecko@003` is worth using over a generic model — it's tuned specifically for retrieval and handles the asymmetry between short queries and long documents well.

```python
import vertexai
from vertexai.language_models import TextEmbeddingModel

class EmbeddingModel:
    def __init__(self, model_name: str = "textembedding-gecko@003"):
        vertexai.init(project="your-project-id", location="us-central1")
        self._model = TextEmbeddingModel.from_pretrained(model_name)

    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        embeddings = self._model.get_embeddings(texts)
        return np.array([e.values for e in embeddings], dtype=np.float32)

    def encode(self, text: str) -> np.ndarray:
        return self.get_embeddings([text])[0]
```

### Step 2: Create a Vector Search index

The numpy store works fine up to maybe 100K docs but past that you need ANN. Vertex AI Matching Engine handles this — Tree-AH gives you sub-linear query time with a small accuracy tradeoff.

```python
from google.cloud import aiplatform

aiplatform.init(project="your-project-id", location="us-central1")

index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name="rag-pipeline-index",
    contents_delta_uri="gs://your-bucket/embeddings/",
    dimensions=768,
    approximate_neighbors_count=10,
    distance_measure_type="COSINE_DISTANCE",
)
```

### Step 3: Deploy to an endpoint

Deploying separately from index creation means you can push a new index version without taking down queries.

```python
index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name="rag-pipeline-endpoint",
    public_endpoint_enabled=True,
)
index_endpoint.deploy_index(index=index, deployed_index_id="rag_pipeline_v1")
```

### Step 4: Swap VectorStore.search()

```python
class VectorStore:
    def __init__(self, endpoint, deployed_index_id: str):
        self._endpoint = endpoint
        self._deployed_index_id = deployed_index_id

    def search(self, query_vec: np.ndarray, top_k: int = 3):
        response = self._endpoint.find_neighbors(
            deployed_index_id=self._deployed_index_id,
            queries=[query_vec.tolist()],
            num_neighbors=top_k,
        )
        return [(n.distance, n.id) for n in response[0]]
```

### Step 5: Swap QueryExpander with Gemini

The template expansion is obviously brittle — it only knows the terms I hardcoded. In prod you'd replace the body of `expand()` with a Gemini call. Cache by query hash to avoid hammering the API on repeated queries.

```python
from vertexai.generative_models import GenerativeModel

class QueryExpander:
    def __init__(self):
        self._model = GenerativeModel("gemini-pro")

    def expand(self, query: str) -> str:
        prompt = (
            "Rewrite the following search query to improve semantic retrieval. "
            "Add synonyms and related technical terms. Return only the expanded query.\n\n"
            f"Query: {query}"
        )
        return self._model.generate_content(prompt).text.strip()
```

### Step 6: IAM

```bash
gcloud iam service-accounts create rag-pipeline-sa

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:rag-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# only needed at index build time, not at query time
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:rag-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### Step 7: Why this structure makes the migration easy

Because each component is its own class with a clear interface, every step above touches exactly one file. `RAGEngine` never changes. You can swap `EmbeddingModel` first, verify it works, then swap `VectorStore`, then `QueryExpander` — independently, in any order.
