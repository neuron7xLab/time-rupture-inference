# NEGATIVE RESULT — v8.1 (pinned, not erased)

**RED.** gap=0.1525 (pinned min 0.25). No threshold tuned.

## Progress vs parent v8
Triggers now fire (1500, precheck PASS, aliasing=0.0833, sodf=1.0) and `history_oracle` (1.7237) MATERIALLY BEATS `scalar_oracle` (2.0338) — scalar-inexpressibility is REAL, not decorative. The frequency defect of v8 is fixed.

## Why still RED (precise root cause)
gap=0.1525<0.25 and history (1.7237) is far from regime (0.7926). Construction B's deterministic carrier (short,short,long,mid×8) is a strong PREDICTABLE cycle the scalar/history oracles (built for a μ-stationary stream) do not model, so whole-stream MAE of BOTH is inflated by carrier error, diluting the gap below 0.25 and preventing history from approaching the noise floor. The scalar-inexpressible signal exists but is masked by carrier variance.

## Disposition
Preserved RED; stronger-model testing stays NOT askable. The fix is a metric/construction correction (trigger-scoped evaluation OR a carrier that is itself scalar-predictable so only the trigger drives the gap) — a NEW v8.2 pre-registration committed before re-run, NOT a v8.1 param edit. Closure-before-restart.
