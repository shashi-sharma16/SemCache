import csv
import json

# Load benchmark
with open("evaluation/benchmark.csv", encoding="utf-8-sig") as file:
    rows = list(csv.DictReader(file))

# Load ShopEase policies
with open("dataset/shopease_policies.json", encoding="utf-8") as file:
    data = json.load(file)

valid_policies = {
    p["policy_id"] for p in data["policies"]
}

# Special classification labels
valid_policies.update({
    "NEEDS_REVIEW",
    "NEEDS_CLARIFICATION"
})

# Load cache seeds
with open("evaluation/cache_seeds.csv", encoding="utf-8-sig") as file:
    seeds = list(csv.DictReader(file))

valid_seeds = {s["seed_id"] for s in seeds}

print("FINAL BENCHMARK INTEGRITY CHECK")
print("-" * 40)

# 1. Invalid policy IDs
invalid_policies = [
    r["query_id"] for r in rows
    if r["expected_policy_id"] not in valid_policies
]
print("Invalid policy IDs:", len(invalid_policies))

# 2. Cacheability consistency
inconsistent = [
    r["query_id"] for r in rows
    if (r["expected_outcome"] == "CACHE_LOOKUP")
    != (r["cacheable"] == "true")
]
print("Cacheability inconsistencies:", len(inconsistent))

# 3. Invalid seed references
invalid_seeds = [
    r["query_id"] for r in rows
    if r["related_query_id"]
    and r["related_query_id"] not in valid_seeds
]
print("Invalid seed references:", len(invalid_seeds))

# 4. Duplicate IDs
ids = [r["query_id"] for r in rows]
print("Duplicate query IDs:", len(ids) - len(set(ids)))

# 5. Source distribution
print("Total benchmark records:", len(rows))
print("Total cache seeds:", len(seeds))

print("-" * 40)

if (
    len(rows) == 100
    and len(seeds) == 6
    and not invalid_policies
    and not inconsistent
    and not invalid_seeds
    and len(ids) == len(set(ids))
):
    print("All final integrity checks passed!")
else:
    print("Integrity check failed. Review the issues.")
