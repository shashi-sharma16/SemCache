
import chromadb
from datetime import datetime, timezone

from backend.core.config import CHROMA_DB_PATH, COLLECTION_NAME


# Connect to persistent ChromaDB
client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))


# Original collection: preserves the initial six cache seeds
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


# Separate collection for the general-purpose semantic cache
general_collection = client.get_or_create_collection(
    name=f"{COLLECTION_NAME}_general",
    metadata={"hnsw:space": "cosine"}
)

# Separate collection: preserves the expanded-cache experiment
expanded_collection = client.get_or_create_collection(
    name=f"{COLLECTION_NAME}_expanded",
    metadata={"hnsw:space": "cosine"}
)


def _add_entry(target_collection, cache_id, query, embedding, answer, policy_id):
    """Store a query, its embedding, and its answer."""

    target_collection.add(
        ids=[cache_id],
        documents=[query],
        embeddings=[embedding],
        metadatas=[{
            "answer": answer,
            "policy_id": policy_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
    )


def add_cache_entry(cache_id, query, embedding, answer, policy_id):
    """Add an entry to the original cache."""

    _add_entry(
        collection, cache_id, query, embedding, answer, policy_id
    )


def add_expanded_cache_entry(cache_id, query, embedding, answer, policy_id):
    """Add an entry to the expanded experimental cache."""

    _add_entry(
        expanded_collection, cache_id, query, embedding, answer, policy_id
    )


def _search_collection(target_collection, embedding, policy_id, n_results=1):
    """Search for a similar query within one policy."""

    matching_count = len(
        target_collection.get(
        where={"policy_id": policy_id}
        )["ids"]
    )

    if matching_count == 0:
        return None

    results = target_collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, matching_count),
        where={"policy_id": policy_id},
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


def search_cache(embedding: list[float], policy_id: str, n_results: int = 1):
    """Search the original cache."""

    return _search_collection(
        collection, embedding, policy_id, n_results
    )


def search_expanded_cache(
    embedding: list[float],
    policy_id: str,
    n_results: int = 1
):
    """Search the expanded experimental cache."""

    return _search_collection(
        expanded_collection, embedding, policy_id, n_results
    )

def add_general_cache_entry(cache_id, query, embedding, answer):
    """Store a generated question-answer pair in the general cache."""

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
    """Find the most semantically similar question in the general cache."""

    if general_collection.count() == 0:
        return None

    results = general_collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, general_collection.count()),
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