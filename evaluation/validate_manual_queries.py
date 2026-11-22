
import csv
from collections import Counter

file_path = "evaluation/manual_queries.csv"

with open(file_path, encoding="utf-8-sig", newline="") as file:
    rows = list(csv.DictReader(file))

required_columns = [
    "query_id",
    "source_row_id",
    "query",
    "query_type",
    "expected_policy_id",
    "expected_outcome",
    "cacheable",
    "related_query_id",
    "source"
]

print("MANUAL QUERY VALIDATION")
print("-" * 40)

# Check columns
with open(file_path, encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    columns = reader.fieldnames

print("Correct columns:", columns == required_columns)

# Check record count
print("Total records:", len(rows))

# Check duplicate IDs
ids = [row["query_id"] for row in rows]
print("Duplicate IDs:", len(ids) - len(set(ids)))

# Check missing required values
required_values = [
    "query_id", "query", "query_type",
    "expected_policy_id", "expected_outcome",
    "cacheable", "source"
]

missing = [
    row["query_id"] for row in rows
    if any(not row[field].strip() for field in required_values)
]
print("Records with missing values:", len(missing))

# Check query type distribution
print("\nQUERY TYPE DISTRIBUTION:")
for name, count in Counter(
    row["query_type"] for row in rows
).items():
    print(name, ":", count)

# Check expected outcome distribution
print("\nEXPECTED OUTCOMES:")
for name, count in Counter(
    row["expected_outcome"] for row in rows
).items():
    print(name, ":", count)

# Check cacheability consistency
inconsistent = [
    row["query_id"] for row in rows
    if (row["expected_outcome"] == "CACHE_LOOKUP")
    != (row["cacheable"] == "true")
]
print("\nInconsistent cacheability:", len(inconsistent))

# Check seed references
valid_seeds = {
    "B009", "B025", "B031",
    "B035", "B041", "B052"
}

invalid_references = [
    row["query_id"] for row in rows
    if row["related_query_id"]
    and row["related_query_id"] not in valid_seeds
]
print("Invalid seed references:", len(invalid_references))

print("-" * 40)

if (
    len(rows) == 40
    and columns == required_columns
    and len(ids) == len(set(ids))
    and not missing
    and not inconsistent
    and not invalid_references
):
    print("All structural validation checks passed!")
else:
    print("Validation failed. Review the issues above.")
