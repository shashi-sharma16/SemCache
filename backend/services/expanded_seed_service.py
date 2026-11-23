import csv

from backend.core.config import BASE_DIR
from backend.services.embedding_service import generate_embedding
from backend.services.policy_service import get_policy
from backend.services.vector_store import (
    add_expanded_cache_entry,
    expanded_collection
)


ORIGINAL_SEED_FILE = BASE_DIR / "evaluation" / "cache_seeds.csv"
ADDITIONAL_SEED_FILE = BASE_DIR / "evaluation" / "expanded_cache_seeds.csv"


def load_expanded_cache_seeds():
    """Load original and additional seeds into the expanded collection."""

    for seed_file in [ORIGINAL_SEED_FILE, ADDITIONAL_SEED_FILE]:
        with open(seed_file, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for seed in reader:
                seed_id = seed["seed_id"]

                # Skip entries that have already been loaded.
                existing = expanded_collection.get(ids=[seed_id])

                if existing["ids"]:
                    continue

                query = seed["query"]
                policy_id = seed["expected_policy_id"]

                policy = get_policy(policy_id)

                if policy is None:
                    raise ValueError(f"Unknown policy ID: {policy_id}")

                embedding = generate_embedding(query)

                add_expanded_cache_entry(
                    cache_id=seed_id,
                    query=query,
                    embedding=embedding,
                    answer=policy["answer"],
                    policy_id=policy_id
                )

    return True
