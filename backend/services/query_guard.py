
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
        r"\b(cancel|cancell?ing|change|update)\b.*\b(my|this|current)\b.*\b(order|purchase)\b",
        r"\b(order|purchase)\b.*\b(cancel|cancell?ing)\b.*\b(immediately|now)\b",
        r"\b(what is|show me|tell me)\s+(?:the\s+)?(?:my|saved)\s+(?:delivery\s+|shipping\s+)?address\b",
        r"\b(address)\b.*\b(saved|stored)\b.*\b(account)\b",
        r"\b(has|have|is|was|were)\b.*\b(order|shipment|delivery|cancellation|refund|shipping address)\b.*\b(shipped|processed|updated|approved|delivered)\b",
        r"\b(has|have)\b.*\b(my|the)\b.*\b(request|order|refund|address)\b.*\b(been|already)\b",
        r"\b(status|progress)\b.*\b(my|the)\b.*\b(order|refund|cancellation)\b",
        r"\b(order|purchase|shipment|delivery)\b.*\b(current|latest|present)\b.*\b(status|eta|location)\b",
        r"\b(eta|estimated time of arrival)\b.*\b(order|purchase|shipment|delivery)\b",
        r"\b(show me|tell me|find|locate)\b.*\b(eta|current status|order status)\b",
        r"\b(check|see)\b.*\b(eta|current status|order status)\b.*\b(for|of)\s+(my|the)\b",
        r"\b(trying to see|trying to check|assistance checking|help me check)\b.*\b(order|purchase)\b.*\b(status|eta)\b",
        r"\b(refund|rebate|restitution|reimburs\w*|money back|refnd)\b.*\b(status|processed|approved|progress|news)\b",
        r"\b(status|progress|news)\b.*\b(refund|rebate|restitution|reimburs\w*|money back|refnd)\b",
        r"\b(cannot afford|can't afford|can not afford|no longer want)\b.*\b(order|purchase)\b",
        r"\b(need|want)\b.*\b(help|assistance)\b.*\b(cancel|cancell?ing)\b.*\b(purchase|purcjase|order)\b",
        r"\b(replace|change|update|edit)\b.*\b(existing|saved|stored|old)\b.*\b(address)\b",
        r"\b(cannot|can't|can not|unable to)\b.*\b(track|locate|find)\b.*\b(order|purchase)\b",
        r"\b(help|assist)\b.*\b(correct|change|update|edit)\b.*\b(delivery|shipping)\s+address\b",
    ]

    for pattern in bypass_patterns:
        if re.search(pattern, text):
            return {
                "decision": "BYPASS_CACHE",
                "reason": "CUSTOMER_SPECIFIC_OR_LIVE_REQUEST"
            }

    # Requests that need more information

    clarify_patterns = [
    r"\b(submit|provide|send)\b.*\b(my|the)\b.*\b(address)\b",
    r"\b(issue|issues|problem|problems|wrong)\b.*\b(refund|address|shipping)\b",
    r"\b(help|assistance)\b.*\b(issue|issues|problem|problems|wrong)\b.*\b(refund|address|shipping)\b",
    r"\b(refund)\b.*\b(issue|issues|problem|problems|help)\b",
    r"^(order|purchase|refund|shipment|delivery)\s+(status|tracking|update)$",
    r"\b(expect|waiting for)\b.*\{\{.*refund amount.*\}\}",
    r"\b(help|assistance)\b.*\b(checking|check|understand)\b.*\b(money back)\b.*\b(policy)\b",
    r"^(canceling|cancelling)\s+order\s+\{\{.*?\}\}$",
    r"\b(question about|question regarding)\b.*\b(cancel|cancell?ing)\b.*\b(order|purchase)\b",
    r"\b(cannot pay|can't pay|can not pay)\b.*\b(purchase|order)\b",
    r"\b(help|assistance)\b.*\b(locate|find|track)\b.*\b(purchaes|purchase|order)\b.*\{\{.*?\}\}",
    r"\b(help|assistance)\b.*\b(set up|setup|add|submit|provide)\b.*\b(new|different|another)\b.*\b(delivery|shipping)\s+address\b",
    r"\b(set|add|submit|provide)\b.*\b(new|different|another)\b.*\b(delivery|shipping)\s+address\b.*\b(help|assistance)\b",
    r"\bhelp\b.*\b(submit\w*|provide|send)\b.*\b(delivery|shipping)\s+address\b",
    r"\b(shipping|delivery)\s+address\s+(issue|problem|error)\b",
]

    for pattern in clarify_patterns:
        if re.search(pattern, text):
            return {
                "decision": "CLARIFY",
                "reason": "INSUFFICIENT_INFORMATION"
            }

    # Questions outside the ShopEase support domain
    support_keywords = [
        "order", "purchase", "refund", "cancel",
        "shipping", "shipment", "delivery", "address",
        "policy", "payment", "return", "tracking",
        "reimbursement", "reimburse", "reimbursed",
        "rebate", "restitution", "money back", "refnd", "refdund"
    ]

    if not any(keyword in text for keyword in support_keywords):
        return {
            "decision": "REVIEW_REQUIRED",
            "reason": "OUT_OF_SUPPORT_SCOPE"
        }

    # Default: allow the semantic cache to evaluate the query
    return {
        "decision": "CACHE_LOOKUP",
        "reason": "GENERAL_POLICY_QUERY"
    }
