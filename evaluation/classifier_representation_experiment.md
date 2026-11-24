
# Classifier Representation Experiment

## Objective
Compare different text representations for semantic policy classification in SemCache.

## Development Dataset
- Source: evaluation/benchmark.csv
- Cacheable queries: 42
- Similarity threshold: 0.40
- Embedding model: all-MiniLM-L6-v2

## Results

| Representation | Correct | Incorrect | Accuracy |
|---|---:|---:|---:|
| Topic only | 42 | 0 | 100.00% |
| Topic + full answer | 40 | 2 | 95.24% |
| Multiple descriptions | 41 | 1 | 97.62% |

## Findings

1. The original topic-only representation performed best.
2. Adding full policy answers introduced additional semantic overlap.
3. Multiple descriptions improved the result over topic + answer, but did not outperform topic only.
4. B054 was misclassified as CHANGE_ADDRESS instead of ADD_ADDRESS by the multiple-description approach.

## Decision

Retain topic-only classification with a threshold of 0.40.

No changes were made to the production classifier.

## Limitations

- Results use a curated development benchmark.
- The threshold was previously selected using the same development queries.
- Development accuracy does not establish real-world generalization.
- The unseen holdout evaluation remains separate and unchanged.
