# EXPECTED OUTPUTS — what a correct run prints

Compare your run to these. Any deviation in a frozen line is a defect
to report, not a quirk to absorb.

## Frozen invariants (byte-identical, any machine)

```
learned post_mae=0.8830 injected=8.0028 oracle=0.7933
win-rate vs injected=1.000  vs best-naive=1.000
gain=0.8680 null_gap=0.0000 win_no=1.000 win_rnd=1.000
```

## Gate lines

```
CLAIMS LINT — PASS (NN files clean)
All checks passed!                       # ruff
Success: no issues found in NN source files   # mypy --strict
NNN passed                               # pytest (exit 0)
PROVENANCE — PASS (NN files; external scan OPEN)
INDI-DEMO :: ALL HARD GATES PASSED — package verified
EXTERNAL-ADVERSARIAL-DEMO :: ALL HARD GATES PASSED — portability stress verified
adversarial portability :: ok=True   escaped_to_pass=[]   missed=[]
```

## Change-detection arc (sealed, not asserted GREEN)

```
#24 predictive_simulation        PARTIAL
#25 calibrated_change_detector   PARTIAL
#26 windowed_change_detector     GREEN
#27 windowed_detector_ood        PARTIAL
#28 carrier_robust_observable    GREEN
#29 portfolio_falsifier          PARTIAL
shape: RED RED GREEN PARTIAL GREEN PARTIAL
```

A PARTIAL/RED here is a *preserved, characterized* result — it keeps
CI green by design (verdict-isolation). It is not a failure of the run.

## Readiness

```
status: CONDITIONALLY_READY
blocking_fact: real_external_collaborator_run = false
```

`READY` must NOT appear until an external run is recorded. If you see
`READY` or `PRODUCTIZABLE` here, that is itself a defect to report.
