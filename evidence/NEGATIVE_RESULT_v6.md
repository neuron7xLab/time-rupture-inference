# NEGATIVE RESULT — v6 precision-weighting (pinned, not erased)

**Verdict: RED / FAIL.** Reported as-is. No threshold tuned.

- aggregate regret fixed=0.0897 precision=0.5422 ratio=6.0459
- win-rate=0.011

## Failing checks
- precision_not_worse_aggregate
- win_rate_vs_fixed
- ablation_must_regress

## Disposition
Frozen v4 untouched. The principled Kalman gain did not beat the heuristic drift-boost on this benchmark — a preserved negative, not a defeat. Intelligence / cognition is explicitly NOT claimed.
