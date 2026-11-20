
import csv
from collections import Counter

file_path = "dataset/raw/bitext_customer_support.csv"

with open(file_path, "r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)

    rows = list(reader)

print("TOTAL RECORDS:", len(rows))

print("\nCOLUMNS:")
print(reader.fieldnames)

print("\nCATEGORY DISTRIBUTION:")
categories = Counter(row["category"] for row in rows)
for category, count in categories.most_common():
    print(category, ":", count)

print("\nNUMBER OF UNIQUE INTENTS:")
intents = Counter(row["intent"] for row in rows)
print(len(intents))

print("\nINTENT DISTRIBUTION:")
for intent, count in intents.most_common():
    print(intent, ":", count)

print("\nFIRST 5 RECORDS:")
for row in rows[:5]:
    print("\nQuestion:", row["instruction"])
    print("Category:", row["category"])
    print("Intent:", row["intent"])
    print("Response:", row["response"])
