import chromadb
from datetime import datetime, timezone

from backend.core.config import CHROMA_DB_PATH, COLLECTION_NAME


# Connect to persistent ChromaDB
client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)

# Create the collection if it doesn't exist
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


def add_cache_entry(
    cache_id: str,
    query: str,
    embedding: list[float],
    answer: str,
    policy_id: str
):
    """Store a query, its embedding, and its answer."""

    collection.add(
        ids=[cache_id],
        documents=[query],
        embeddings=[embedding],
        metadatas=[{
            "answer": answer,
            "policy_id": policy_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
    )


def search_cache(embedding: list[float], n_results: int = 1):
    """Find the most semantically similar cached query."""

    if collection.count() == 0:
        return None

    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, collection.count()),
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