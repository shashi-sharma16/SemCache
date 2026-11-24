import csv
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_DIR = Path(__file__).resolve().parents[1]

BENCHMARK_FILE = BASE_DIR / "evaluation" / "benchmark.csv"
REFERENCE_FILE = BASE_DIR / "evaluation" / "guard_development.csv"
RESULT_FILE = BASE_DIR / "evaluation" / "api_benchmark_results.csv"

API_URL = "http://127.0.0.1:8000/query"
REQUEST_TIMEOUT = 300


FIELDS = [
    "query_id",
    "query",
    "expected_outcome",
    "actual_decision",
    "routing_correct",
    "expected_policy_id",
    "actual_policy_id",
    "policy_correct",
    "reason",
    "cache_hit",
    "similarity",
    "latency_seconds",
    "status",
    "answer",
    "error"
]


def save_results(results):
    with open(RESULT_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)


def send_query(query):
    body = json.dumps({"query": query}).encode("utf-8")

    request = Request(
        API_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))

        latency = time.perf_counter() - start

        return result, latency, ""

    except (HTTPError, URLError, TimeoutError, OSError) as error:
        latency = time.perf_counter() - start
        return {}, latency, str(error)


def run_api_benchmark():

    with open(BENCHMARK_FILE, "r", encoding="utf-8-sig", newline="") as file:
        queries = list(csv.DictReader(file))

    with open(REFERENCE_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reference = {
            row["query_id"]: row
            for row in csv.DictReader(file)
        }

    results = []

    if RESULT_FILE.exists():
        with open(RESULT_FILE, "r", encoding="utf-8-sig", newline="") as file:
            results = list(csv.DictReader(file))

    completed_ids = {
        row["query_id"]
        for row in results
        if row["status"] == "SUCCESS"
    }

    print("Total benchmark queries:", len(queries))
    print("Already completed:", len(completed_ids))
    print("Remaining:", len(queries) - len(completed_ids))
    print("-" * 55, flush=True)

    for index, query_row in enumerate(queries, start=1):

        query_id = query_row["query_id"]

        if query_id in completed_ids:
            continue

        expected = reference.get(query_id)

        if expected is None:
            print(f"{query_id}: Missing audited reference. Skipping.")
            continue

        query = query_row["query"]
        expected_outcome = expected["expected_outcome"]
        expected_policy = expected["expected_policy_id"]

        response, latency, error = send_query(query)

        if error:
            result = {
                "query_id": query_id,
                "query": query,
                "expected_outcome": expected_outcome,
                "actual_decision": "",
                "routing_correct": "",
                "expected_policy_id": expected_policy,
                "actual_policy_id": "",
                "policy_correct": "",
                "reason": "",
                "cache_hit": "",
                "similarity": "",
                "latency_seconds": round(latency, 4),
                "status": "ERROR",
                "answer": "",
                "error": error
            }

        else:
            actual_decision = response.get("decision", "")
            actual_policy = response.get("policy_id", "")

            policy_correct = (
                actual_policy == expected_policy
                if expected_outcome == "CACHE_LOOKUP"
                else ""
            )

            result = {
                "query_id": query_id,
                "query": query,
                "expected_outcome": expected_outcome,
                "actual_decision": actual_decision,
                "routing_correct": actual_decision == expected_outcome,
                "expected_policy_id": expected_policy,
                "actual_policy_id": actual_policy,
                "policy_correct": policy_correct,
                "reason": response.get("reason", ""),
                "cache_hit": response.get("cache_hit", False),
                "similarity": response.get("similarity", ""),
                "latency_seconds": round(latency, 4),
                "status": "SUCCESS",
                "answer": response.get("answer", ""),
                "error": ""
            }

        results.append(result)

        # Save after every request so completed work is preserved.
        save_results(results)

        print(
            f"[{index}/{len(queries)}] {query_id} | "
            f"Expected: {expected_outcome} | "
            f"Actual: {result['actual_decision']} | "
            f"Status: {result['status']}",
            flush=True
        )

    print("\nAPI evaluation finished.")
    print("Successful requests:", sum(r["status"] == "SUCCESS" for r in results))
    print("Failed requests:", sum(r["status"] == "ERROR" for r in results))
    print("Results saved to:", RESULT_FILE)


if __name__ == "__main__":
    run_api_benchmark()
