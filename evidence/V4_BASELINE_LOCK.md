# V4 BASELINE LOCK — frozen at release v0.1.0

This release **is** the v4 freeze (methodology PR-1). Nothing in the
proven core may change without a new pre-registered lineage.

| field | value |
|---|---|
| frozen tag | `cti-os-v4-GREEN` → released as `v0.1.0` |
| proven | error-driven online update + drift detection adapts to a hidden temporal regime shift better than injected / frozen / naive baselines |
| status | **valid temporal adaptation proof** (prediction-error temporal adaptation) |
| NOT proven | that an agent *action* causally changes the future state distribution |
| grid | 30 seeds × 3 shift magnitudes (incl. decrease) |
| headline | learned post_shift_mae 0.883 vs injected 8.003 vs oracle 0.793; win-rate 1.000 |
| scientific thresholds | byte-identical v2→v4 (`git show cti-os-v2-GREEN:prereg/preregistration.yaml`) |

**Locked claim boundary (verbatim, governs all downstream work):**

Allowed:
> The learned agent adapts to hidden temporal regime shifts better than
> fixed and naive baselines under preregistered metrics, deterministic
> replay, no-leakage constraints, and ablation controls.

Forbidden:
> The agent has intelligence, consciousness, biological neuroplasticity,
> or understanding of time.

The causal step — *error updates belief, belief teaches action to change
the future* — is the **next** pre-registered lineage (v5 / Causal
Temporal Inference Core). It is deliberately NOT started in v0.1:
closure-before-restart, anti-overengineering.
