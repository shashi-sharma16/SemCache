
import csv
from collections import Counter

file_path = "dataset/raw/bitext_customer_support.csv"

with open(file_path, "r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

flags = Counter(row["flags"] for row in rows)

print("FLAG DISTRIBUTION:")
for flag, count in flags.most_common():
    print(f"{flag}: {count}")

print("\nSAMPLE QUESTIONS BY FLAG:")

for flag, count in flags.most_common(10):
    print(f"\nFLAG: {flag} ({count} records)")

    samples = [
        row for row in rows if row["flags"] == flag
    ]

    for row in samples[:2]:
        print("-", row["instruction"])
