# v6 Precision-Weighting — Release Gate

**Verdict: RED / FAIL**

- aggregate regret  fixed=0.0897  precision=0.5422  ratio=6.0459 (max 1.0)
- win-rate precision<fixed: 0.011 (min 0.6)

## Checks
- [ ] precision_not_worse_aggregate
- [ ] win_rate_vs_fixed
- [ ] ablation_must_regress
- [x] deterministic_replay

Operational analogy only (scalar Kalman / predictive-coding precision weighting); NOT a biological claim.