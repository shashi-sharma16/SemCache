
from backend.core.config import SIMILARITY_THRESHOLD
from backend.services.embedding_service import generate_embedding
from backend.services.vector_store import search_cache, search_expanded_cache


def _lookup(
    query: str,
    policy_id: str,
    search_function,
    threshold: float
):
    """Shared logic for original and expanded cache lookups."""

    embedding = generate_embedding(query)

    result = search_function(
        embedding=embedding,
        policy_id=policy_id
    )

    if result is None:
        return {
            "cache_hit": False,
            "reason": "NO_MATCHING_POLICY_ENTRY"
        }

    similarity = max(0.0, min(1.0, 1 - result["distance"]))

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
        "policy_id": result["metadata"]["policy_id"],
        "similarity": similarity
    }


def lookup_cache(
    query: str,
    policy_id: str,
    threshold: float = SIMILARITY_THRESHOLD
):
    """Search the original cache."""

    return _lookup(query, policy_id, search_cache, threshold)


def lookup_expanded_cache(
    query: str,
    policy_id: str,
    threshold: float = SIMILARITY_THRESHOLD
):
    """Search the expanded experimental cache."""

    return _lookup(query, policy_id, search_expanded_cache, threshold)
