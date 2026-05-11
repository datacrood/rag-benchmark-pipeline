# run with: python -m rag.benchmark

import json
from pathlib import Path

from tabulate import tabulate

from data.corpus import CHUNKS
from rag.embeddings import EmbeddingModel
from rag.storage import VectorStore
from rag.retrieval import QueryExpander, RAGEngine


BENCHMARK_QUERIES = [
    "How does the system handle peak load?",
    "What happens when a node fails in the cluster?",
    "How is data secured during transmission?",
]

REPO_ROOT = Path(__file__).parent.parent


def build_engine() -> RAGEngine:
    em = EmbeddingModel()
    store = VectorStore()
    expander = QueryExpander()
    engine = RAGEngine(em, store, expander)
    engine.ingest(CHUNKS)
    return engine


def run_benchmark(engine: RAGEngine) -> list[dict]:
    records = []
    for query in BENCHMARK_QUERIES:
        result_a = engine.retrieve(query, strategy="A", top_k=3)
        result_b = engine.retrieve(query, strategy="B", top_k=3)

        chunks_a = {r[1] for r in result_a["results"]}
        chunks_b = {r[1] for r in result_b["results"]}
        only_in_a = chunks_a - chunks_b
        only_in_b = chunks_b - chunks_a

        records.append({
            "query": query,
            "strategy_a": [
                {"rank": i + 1, "score": round(s, 4), "chunk": c[:120]}
                for i, (s, c) in enumerate(result_a["results"])
            ],
            "strategy_b": {
                "expanded_query": result_b["expanded_query"],
                "results": [
                    {"rank": i + 1, "score": round(s, 4), "chunk": c[:120]}
                    for i, (s, c) in enumerate(result_b["results"])
                ],
            },
            "diff": {
                "only_in_a": list(only_in_a),
                "only_in_b": list(only_in_b),
                "overlap_count": len(chunks_a & chunks_b),
            },
        })
    return records


def build_markdown(records: list[dict]) -> str:
    lines = [
        "# Retrieval Benchmark: Strategy A vs Strategy B\n",
        "**Corpus:** 10 cloud infrastructure technical paragraphs  ",
        "**Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers)  ",
        "**Similarity metric:** Cosine similarity (L2-normalize + dot product)  ",
        "**Strategy A:** Raw embedding of original query  ",
        "**Strategy B:** Template-expanded query before embedding  \n",
        "---\n",
    ]

    for rec in records:
        lines.append(f"## Query: *{rec['query']}*\n")
        lines.append(f"**Strategy B expanded query:**  \n`{rec['strategy_b']['expanded_query']}`\n")

        table_rows = []
        for r in rec["strategy_a"]:
            table_rows.append(["A", r["rank"], f"{r['score']:.4f}", r["chunk"]])
        for r in rec["strategy_b"]["results"]:
            table_rows.append(["B", r["rank"], f"{r['score']:.4f}", r["chunk"]])

        lines.append(
            tabulate(
                table_rows,
                headers=["Strategy", "Rank", "Score", "Chunk (first 120 chars)"],
                tablefmt="github",
            )
        )
        lines.append("")

        diff = rec["diff"]
        lines.append(f"\n**Overlap:** {diff['overlap_count']}/3 chunks shared between strategies")
        if diff["only_in_b"]:
            lines.append(f"\n**Only in Strategy B (new retrievals from expansion):**")
            for c in diff["only_in_b"]:
                lines.append(f"- _{c[:100]}..._")
        if diff["only_in_a"]:
            lines.append(f"\n**Only in Strategy A (lost after expansion):**")
            for c in diff["only_in_a"]:
                lines.append(f"- _{c[:100]}..._")
        lines.append("\n---\n")

    return "\n".join(lines)


def main():
    print("loading model and ingesting corpus...")
    engine = build_engine()
    records = run_benchmark(engine)

    with open(REPO_ROOT / "benchmark_results.json", "w") as f:
        json.dump(records, f, indent=2)

    md_content = build_markdown(records)
    with open(REPO_ROOT / "retrieval_benchmark.md", "w") as f:
        f.write(md_content)

    print(md_content)


if __name__ == "__main__":
    main()
