
from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from backend.services.query_guard import guard_query
from backend.services.policy_classifier import identify_policy
from backend.services.policy_service import get_policy
from backend.services.cache_service import lookup_expanded_cache


router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Customer support query"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty or contain only whitespace.")

        return value

@router.post("/query")
def process_query(request: QueryRequest):

    query = request.query.strip()

    # Step 1: Query Guard
    guard_result = guard_query(query)
    decision = guard_result["decision"]

    if decision == "CLARIFY":
        return {
            "decision": decision,
            "reason": guard_result["reason"],
            "answer": "Could you please provide more details about your request?",
            "cache_hit": False
        }

    if decision == "REVIEW_REQUIRED":
        return {
            "decision": decision,
            "reason": guard_result["reason"],
            "answer": "This request is outside the supported ShopEase policy scope.",
            "cache_hit": False
        }

    if decision == "BYPASS_CACHE":
        return {
            "decision": decision,
            "reason": guard_result["reason"],
            "answer": (
                "This request requires customer-specific information. "
                "Please contact ShopEase support or use its authenticated "
                "support system."
            ),
            "cache_hit": False
        }

    # Step 2: Identify policy
    classification = identify_policy(query)

    if not classification["identified"]:
        return {
            "decision": "REVIEW_REQUIRED",
            "reason": "POLICY_NOT_IDENTIFIED",
            "answer": "I could not identify a suitable ShopEase policy for this request.",
            "cache_hit": False,
            "policy_similarity": classification["similarity"]
        }

    policy_id = classification["policy_id"]

    # Step 3: Search expanded semantic cache
    cache_result = lookup_expanded_cache(
        query=query,
        policy_id=policy_id
    )

    if cache_result["cache_hit"]:
        return {
            "decision": decision,
            "reason": "SEMANTIC_CACHE_HIT",
            "answer": cache_result["answer"],
            "cache_hit": True,
            "policy_id": policy_id,
            "similarity": cache_result["similarity"],
            "matched_query": cache_result["matched_query"]
        }

    # Step 4: Cache miss - return the authoritative policy answer
    policy = get_policy(policy_id)

    if not policy:
        return {
            "decision": "REVIEW_REQUIRED",
            "reason": "POLICY_NOT_FOUND",
            "answer": "The requested ShopEase policy could not be retrieved.",
            "cache_hit": False,
            "policy_id": policy_id
        }

    return {
        "decision": decision,
        "reason": "CACHE_MISS",
        "answer": policy["answer"],
        "cache_hit": False,
        "policy_id": policy_id,
        "similarity": cache_result.get("similarity")
    }
