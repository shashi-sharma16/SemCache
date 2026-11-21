
import csv
import json
from pathlib import Path
from collections import Counter

# Locate project files
BASE_DIR = Path(__file__).resolve().parent.parent

MAPPING_FILE = BASE_DIR / "dataset" / "query_policy_mapping.csv"
DATASET_FILE = BASE_DIR / "dataset" / "bitext_selected_60.csv"
POLICY_FILE = BASE_DIR / "dataset" / "shopease_policies.json"

# Read all three files
with open(MAPPING_FILE, encoding="utf-8", newline="") as file:
    mapping = list(csv.DictReader(file))

with open(DATASET_FILE, encoding="utf-8", newline="") as file:
    dataset = list(csv.DictReader(file))

with open(POLICY_FILE, encoding="utf-8") as file:
    policies = json.load(file)["policies"]

errors = []

# 1. Check total records
if len(mapping) != 60:
    errors.append(f"Expected 60 records, found {len(mapping)}")

# 2. Check required columns
required_columns = {
    "query_id",
    "source_row_id",
    "query",
    "expected_policy_id",
    "cacheable",
    "review_status"
}

if mapping:
    missing_columns = required_columns - set(mapping[0].keys())

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

# 3. Check duplicate query IDs
query_ids = [row["query_id"] for row in mapping]
duplicates = [
    key for key, count in Counter(query_ids).items()
    if count > 1
]

if duplicates:
    errors.append(f"Duplicate query IDs: {duplicates}")

# 4. Check that all 60 query IDs exist
expected_ids = {f"Q{i:03d}" for i in range(1, 61)}

if set(query_ids) != expected_ids:
    errors.append("Query IDs are missing or incorrectly formatted")

# 5. Check original source row references
source_lookup = {
    row["source_row_id"]: row["instruction"]
    for row in dataset
}

for row in mapping:
    source_id = row["source_row_id"]

    if source_id not in source_lookup:
        errors.append(
            f"{row['query_id']}: Invalid source row ID {source_id}"
        )
    else:
        original_query = source_lookup[source_id].strip()
        mapped_query = row["query"].strip()

        if original_query != mapped_query:
            errors.append(
                f"{row['query_id']}: Query does not exactly "
                f"match source row {source_id}"
            )

# 6. Check valid policy IDs
valid_policy_ids = {
    policy["policy_id"] for policy in policies
}

valid_policy_ids.update({
    "NEEDS_REVIEW",
    "NEEDS_CLARIFICATION"
})

for row in mapping:
    if row["expected_policy_id"] not in valid_policy_ids:
        errors.append(
            f"{row['query_id']}: Invalid policy ID "
            f"{row['expected_policy_id']}"
        )

# 7. Check cacheability values
for row in mapping:
    if row["cacheable"].lower() not in {"true", "false"}:
        errors.append(
            f"{row['query_id']}: Invalid cacheable value"
        )

# 8. Check review status
valid_statuses = {"provisional", "unresolved", "verified"}

for row in mapping:
    if row["review_status"] not in valid_statuses:
        errors.append(
            f"{row['query_id']}: Invalid review status"
        )

# Display results
print("\nSEMCache MAPPING VALIDATION")
print("-" * 35)

print("Mapping records:", len(mapping))
print("Selected dataset records:", len(dataset))
print("Available policies:", len(policies))

if errors:
    print("\nVALIDATION ISSUES FOUND:")

    for error in errors:
        print("-", error)

    print(f"\nTotal issues: {len(errors)}")

else:
    print("\nAll structural validation checks passed!")
