import chromadb
from datetime import datetime, timezone

from backend.core.config import CHROMA_DB_PATH, COLLECTION_NAME


# Connect to persistent ChromaDB
client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))


# General-purpose semantic cache
general_collection = client.get_or_create_collection(
    name=f"{COLLECTION_NAME}_general",
    metadata={"hnsw:space": "cosine"}
)


def add_general_cache_entry(cache_id, query, embedding, answer):
    """Store a generated question-answer pair."""

    general_collection.add(
        ids=[cache_id],
        documents=[query],
        embeddings=[embedding],
        metadatas=[{
            "answer": answer,
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
    )


def search_general_cache(embedding: list[float], n_results: int = 1):
    """Find the most semantically similar cached question."""

    count = general_collection.count()

    if count == 0:
        return None

    results = general_collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, count),
        include=["documents", "metadatas", "distances"]
    )

    if not results["ids"][0]:
        return None

    return {
        "id": results["ids"][0][0],
        "query": results["documents"][0][0],
        "metadata": results["metadatas"][0][0],
        "distance": results["distances"][0][0]
    }