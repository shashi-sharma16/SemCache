
from backend.services.embedding_service import generate_embedding
from backend.services.policy_service import load_policies


CACHEABLE_POLICY_IDS = {
    "ORDER_TRACKING",
    "REFUND_ELIGIBILITY",
    "REFUND_TIMELINE",
    "CANCEL_ORDER",
    "CHANGE_ADDRESS",
    "ADD_ADDRESS"
}


def identify_policy(query: str, threshold: float = 0.40):
    """Identify the most relevant cacheable ShopEase policy."""

    policies = load_policies()
    query_embedding = generate_embedding(query)

    best_policy = None
    best_similarity = -1.0

    for policy_id in CACHEABLE_POLICY_IDS:
        policy = policies[policy_id]
        topic_embedding = generate_embedding(policy["topic"])

        similarity = sum(
            a * b for a, b in zip(query_embedding, topic_embedding)
        )

        if similarity > best_similarity:
            best_similarity = similarity
            best_policy = policy_id

    if best_similarity < threshold:
        return {
            "policy_id": None,
            "similarity": best_similarity,
            "identified": False
        }

    return {
        "policy_id": best_policy,
        "similarity": best_similarity,
        "identified": True
    }
