from backend.core.config import SIMILARITY_THRESHOLD
from backend.services.embedding_service import generate_embedding
from backend.services.vector_store import search_cache


def lookup_cache(query: str, threshold: float = SIMILARITY_THRESHOLD):
    """Check whether a semantically similar cached answer exists."""

    # Convert the incoming query into an embedding
    embedding = generate_embedding(query)

    # Search for the closest cached query
    result = search_cache(embedding)

    # No cached entries found
    if result is None:
        return {
            "cache_hit": False,
            "reason": "CACHE_EMPTY"
        }

    # ChromaDB uses cosine distance, not similarity
    similarity = max(0.0, min(1.0, 1 - result["distance"]))

    # Check whether the match meets our threshold
    if similarity >= threshold:
        return {
            "cache_hit": True,
            "answer": result["metadata"]["answer"],
            "matched_query": result["query"],
            "policy_id": result["metadata"]["policy_id"],
            "similarity": similarity
        }

    return {
        "cache_hit": False,
        "reason": "SIMILARITY_BELOW_THRESHOLD",
        "matched_query": result["query"],
        "similarity": similarity
    }