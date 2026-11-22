
import csv
import json
from collections import Counter

# Load the Bitext review records
with open("evaluation/bitext_review.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

# Load valid ShopEase policy IDs
with open("dataset/shopease_policies.json", encoding="utf-8") as file:
    data = json.load(file)

valid_policies = {p["policy_id"] for p in data["policies"]}

print("BITEXT REVIEW VALIDATION")
print("-" * 35)

# 1. Record count
print("Total records:", len(rows))

# 2. Missing fields
missing = [
    r["query_id"] for r in rows
    if any(not value for value in r.values())
]
print("Records with missing fields:", len(missing))

# 3. Duplicate IDs
query_ids = [r["query_id"] for r in rows]
source_ids = [r["source_row_id"] for r in rows]

print("Duplicate query IDs:", len(query_ids) - len(set(query_ids)))
print("Duplicate source IDs:", len(source_ids) - len(set(source_ids)))

# 4. Outcome and cacheability consistency
inconsistent = [
    r for r in rows
    if (r["expected_outcome"] == "CACHE_LOOKUP")
    != (r["cacheable"] == "true")
]
print("Inconsistent cacheability records:", len(inconsistent))

# 5. Unknown policy IDs
used_policies = {
    r["expected_policy_id"] for r in rows
    if r["expected_policy_id"] not in (
        "NEEDS_CLARIFICATION",
        "NEEDS_REVIEW"
    )
}

unknown = used_policies - valid_policies
print("Unknown policy IDs:", sorted(unknown))

print("-" * 35)

if not missing and not inconsistent and not unknown:
    print("All validation checks passed!")
else:
    print("Some validation checks failed. Review the results.")
