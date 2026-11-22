import csv

file_path = "evaluation/manual_queries.csv"

seed_mapping = {
    "B009": "S001",
    "B025": "S002",
    "B031": "S003",
    "B035": "S004",
    "B041": "S005",
    "B052": "S006"
}

with open(file_path, encoding="utf-8-sig", newline="") as file:
    rows = list(csv.DictReader(file))
    columns = list(rows[0].keys())

updated = 0

for row in rows:
    old_reference = row["related_query_id"]

    if old_reference in seed_mapping:
        row["related_query_id"] = seed_mapping[old_reference]
        updated += 1

with open(file_path, "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print("Seed references updated:", updated)
print("Total records:", len(rows))
