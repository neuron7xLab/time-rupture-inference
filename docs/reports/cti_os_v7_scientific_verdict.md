# CTI-OS v7 — Scientific Verdict (PR #3)

**VERDICT: RED**

Decision rule (pre-registered, unchanged): a learned model (`esn_small` / `linear_ssm_small`) must beat BOTH the frozen v4 heuristic AND the AR baseline on aggregate post-shift MAE, with win-rate ≥ 0.6 vs each, holding on every shift, across 30 seeds, deterministic, finite.

- agg post_shift_mae  heuristic_v4=0.9285  ar_baseline=0.9413
- esn_small: agg=1.0110  wr_vs_heuristic=0.156  wr_vs_baseline=0.256  passes=False
- linear_ssm_small: agg=1.3211  wr_vs_heuristic=0.022  wr_vs_baseline=0.089  passes=False
- deterministic_replay=True  finite=True

Claim boundary: a learned reservoir-readout sequence model with a representational advantage on a harder nonstationary task — NOT intelligence, NOT cognition, NOT AGI.

```json
{
  "verdict": "RED",
  "winner": null,
  "agg_heuristic_v4": 0.9284718613298512,
  "agg_ar_baseline": 0.9412557142571444,
  "learned": {
    "esn_small": {
      "agg": 1.0109640079774387,
      "wr_vs_heuristic": 0.15555555555555556,
      "wr_vs_baseline": 0.25555555555555554,
      "passes": false
    },
    "linear_ssm_small": {
      "agg": 1.3211167884345705,
      "wr_vs_heuristic": 0.022222222222222223,
      "wr_vs_baseline": 0.08888888888888889,
      "passes": false
    }
  },
  "deterministic_replay": true,
  "finite_metrics": true,
  "grid": "30 seeds x 3 shifts"
}
```