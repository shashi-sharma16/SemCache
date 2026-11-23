# Expanded Cache Experiment

## Objective
Evaluate whether adding carefully curated seed queries improves semantic cache coverage while maintaining cache precision.

## Experimental Setup
- Benchmark queries: 100
- Original cache seeds: 6
- Additional cache seeds: 8
- Expanded cache seeds: 14
- Similarity thresholds: 0.75, 0.80, 0.85, 0.90, 0.95
- Same Query Guard, policy classifier, and benchmark used in both experiments.

## Results

| Threshold | Original Correct Hits | Expanded Correct Hits | Additional Hits |
|---|---:|---:|---:|
| 0.75 | 20 | 25 | +5 |
| 0.80 | 14 | 20 | +6 |
| 0.85 | 11 | 16 | +5 |
| 0.90 | 4 | 8 | +4 |
| 0.95 | 1 | 4 | +3 |

Both configurations recorded 1.000 precision and zero false cache hits at all tested thresholds.

## Newly Recovered Queries at Threshold 0.75

| Query ID | Policy | Similarity |
|---|---|---:|
| M008 | REFUND_ELIGIBILITY | 0.841 |
| M009 | REFUND_ELIGIBILITY | 1.000 |
| M012 | REFUND_TIMELINE | 1.000 |
| M015 | CHANGE_ADDRESS | 0.953 |
| M017 | CHANGE_ADDRESS | 0.867 |

## Findings

The expanded cache improved correct cache hits at every tested threshold.

At threshold 0.75:
- Original cache recall: 47.6%
- Expanded cache recall: 59.5%
- Improvement: 11.9 percentage points
- Additional correct cache hits: 5

No false cache hits were observed in this benchmark.

## Limitations
- Results are based on a curated 100-query benchmark.
- The additional seeds were manually selected.
- The policy classifier threshold was tuned using the same benchmark.
- These results do not establish generalization to unseen real-world queries.
- Independent testing is required before making broader accuracy claims.

## Conclusion

Adding eight carefully selected seed queries improved semantic cache coverage while preserving observed precision on the existing benchmark. The expanded cache is a promising improvement over the original six-seed configuration.
