# NEGATIVE RESULT — lineage v1 (pinned, not erased)

**Verdict: RED / FAIL.** Reported as-is. No threshold was tuned.

prereg_hash (v1): `55f90a8e376598a7c795be13eaf6307933567aa3f60757f332924bf1787fea30`
pinned commit: `3c23f59` (predates run — integrity intact).

## Result (16 seeds, aggregate)

| agent | post_shift_mae |
|---|---|
| oracle (upper bound) | 0.792 |
| exp_smoothing | 0.999 |
| moving_average | 1.037 |
| **learned_full** | **1.120** |
| last_interval | 1.144 |
| injected (strawman) | 7.002 |

learned beat injected on 16/16 seeds, but **lost to the best naive
baseline on 0/16**.

## Root cause (instrument defect, not hypothesis refutation)

1. **Drift detector provably inert:** `learned_full` metrics are
   byte-identical to `learned_no_drift`; Page-Hinkley fired on 0/16 seeds.
2. **Mechanism:** the cold-start transient (prior=1 vs true interval≈10
   ⇒ |error|≈9 during warmup) inflates the Page-Hinkley running mean, so
   the post-shift jump (|error|≈7) never exceeds the poisoned baseline.
3. **Consequence:** with the boost dead, the learner adapts only at
   `base_gain=0.06` (slow creep), accruing a large transient bias over
   the 250-step horizon ⇒ loses to exponential smoothing.

## Disposition

The hypothesis (an error-driven learner beats injected + baseline
post-shift) is **not** refuted — the v1 estimator/detector is
under-powered. Lineage **v2** opens with a corrected detector
(Page-Hinkley enabled and re-baselined *after* warmup), under the
**identical** pre-registered success thresholds, env, and metrics. Only
`src/ctios/agents.py` estimator internals change. This v1 RED is
committed and tagged before v2 begins.
