
# Query Guard – Benchmark Review

## Overview

The Query Guard benchmark contains 100 questions.
After the latest rule updates, 9 mismatches remain.

These cases were manually reviewed to understand whether the
actual routing decisions are reasonable.

The original benchmark labels have not been modified.

## Reviewed Cases

| Query ID | Expected | Actual | Review |
|---|---|---|---|
| B005 | REVIEW_REQUIRED | BYPASS_CACHE | Customer-specific tracking |
| B019 | REVIEW_REQUIRED | CLARIFY | Refund issue needs details |
| B039 | REVIEW_REQUIRED | CACHE_LOOKUP | General reimbursement policy |
| B043 | REVIEW_REQUIRED | BYPASS_CACHE | Existing address correction |
| B045 | REVIEW_REQUIRED | CLARIFY | Address issue needs details |
| B051 | REVIEW_REQUIRED | CLARIFY | Address setup issue needs details |
| B053 | REVIEW_REQUIRED | CLARIFY | Secondary address issue needs details |
| B060 | REVIEW_REQUIRED | CLARIFY | Insufficient information |
| H009 | REVIEW_REQUIRED | BYPASS_CACHE | Personal saved address request |

## Key Observations

1. Customer-specific requests should bypass generic cache lookup.
2. Vague requests should ask for clarification.
3. General policy questions can be considered for cache lookup.
4. Similar wording does not always mean the same answer is safe to reuse.

## Evaluation Notes

- Original benchmark labels are preserved.
- The nine cases are recorded as reviewed disagreements.
- These manual assessments are not independent validation of the original labels.
- Further evaluation is required during end-to-end integration.
