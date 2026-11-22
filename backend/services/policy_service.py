import json

from backend.core.config import BASE_DIR


POLICY_FILE = BASE_DIR / "dataset" / "shopease_policies.json"


def load_policies() -> dict:
    """Load ShopEase policies from the JSON knowledge base."""

    with open(POLICY_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        policy["policy_id"]: policy
        for policy in data["policies"]
    }


def get_policy(policy_id: str) -> dict | None:
    """Retrieve a policy using its policy ID."""

    policies = load_policies()

    return policies.get(policy_id)