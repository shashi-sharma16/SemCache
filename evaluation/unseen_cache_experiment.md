
# Unseen End-to-End Cache Evaluation

## Objective
Evaluate SemCache's Query Guard, Policy Classifier, and expanded semantic cache on 50 previously unseen, manually curated queries.

## Evaluation Setup
- Unseen queries: 50
- Expanded cache entries: 14
- Embedding model: all-MiniLM-L6-v2
- Similarity thresholds: 0.75, 0.80, 0.85, 0.90, 0.95
- Cache entries were not modified during evaluation.
- Unseen queries were not added to the cache.

## Component Results

| Component | Result |
|---|---:|
| Query Guard | 42/50 (84%) |
| Policy Classifier (standalone) | 22/25 (88%) |
| Policy Classifier (after guard routing) | 21/24 (87.5%) |

## End-to-End Cache Results

| Threshold | Correct Hits | False Hits | Precision | Recall |
|---|---:|---:|---:|---:|
| 0.75 | 7 | 1 | 87.5% | 28% |
| 0.80 | 4 | 0 | 100% | 16% |
| 0.85 | 1 | 0 | 100% | 4% |
| 0.90 | 0 | 0 | N/A | 0% |
| 0.95 | 0 | 0 | N/A | 0% |

## False Cache Hit Analysis

Query U034:

"What is the latest tracking location for my order?"

- Expected decision: BYPASS_CACHE
- Actual guard decision: CACHE_LOOKUP
- Identified policy: ORDER_TRACKING
- Matched policy: ORDER_TRACKING
- Similarity: 0.7627

The guard failed to recognize a customer-specific live tracking request. The classifier then assigned it to the general ORDER_TRACKING policy, allowing an inappropriate cache hit.

## Findings

1. The guard achieved 84% accuracy on the unseen holdout.
2. The classifier achieved 88% standalone accuracy on unseen cacheable queries.
3. At threshold 0.75, the expanded cache returned seven correct hits and one false hit.
4. Increasing the threshold reduced false hits but also reduced recall.
5. Customer-specific requests must be reliably intercepted before semantic classification and cache lookup.

## Limitations

- The holdout is manually curated, not production traffic.
- Results represent one fixed set of 14 cache entries.
- The dataset is small and does not establish real-world performance.
- Thresholds and classifier settings were selected using the development benchmark.
- No live customer order system or external LLM was involved.

## Decision

Preserve this evaluation as the initial unseen baseline.

Do not modify the holdout labels or tune the system against these test queries. Future guard improvements should be evaluated on a separate development dataset.
