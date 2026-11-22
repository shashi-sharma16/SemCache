import re


def guard_query(query: str) -> dict:
    """Decide whether a query is safe for semantic cache lookup."""

    text = query.lower().strip()

    # Empty queries need clarification
    if not text:
        return {
            "decision": "CLARIFY",
            "reason": "EMPTY_QUERY"
        }

    # Requests involving live or customer-specific information
    bypass_patterns = [
        r"\b(current|currently|right now)\b.*\b(order|refund|delivery|shipment)\b",
        r"\b(status|approval status)\b.*\b(order|refund)\b",
        r"\b(has my refund|is my refund|where is my order)\b",
        r"\b(cancel|cancell?ing|change|update)\b.*\b(my|this|current)\b.*\b(order|purchase|address)\b",
        r"\b(order|purchase)\b.*\b(cancel|cancell?ing)\b.*\b(immediately|now)\b",
        r"\{\{.*?\}\}"
    ]

    for pattern in bypass_patterns:
        if re.search(pattern, text):
            return {
                "decision": "BYPASS_CACHE",
                "reason": "CUSTOMER_SPECIFIC_OR_LIVE_REQUEST"
            }

    # Requests that are too ambiguous to answer safely
    clarify_patterns = [
        r"\b(submit|provide|send|enter)\b.*\b(my|the)\b.*\b(address)\b"
    ]

    for pattern in clarify_patterns:
        if re.search(pattern, text):
            return {
                "decision": "CLARIFY",
                "reason": "AMBIGUOUS_ADDRESS_REQUEST"
            }

    # Default: allow the semantic cache to evaluate the query
    return {
        "decision": "CACHE_LOOKUP",
        "reason": "GENERAL_POLICY_QUERY"
    }
