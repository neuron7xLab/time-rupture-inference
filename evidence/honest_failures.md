# Honest failures register — CTI-OS proof-of-life

Run is GREEN. Acknowledged residual limitations (not papered over):

- Single synthetic environment family (step change in a Gaussian interval). Generality across regime shapes is untested → next lineage.
- `last_interval` adapts instantly but is noise-dominated; learned wins on variance, not on adaptation latency alone — claim scoped accordingly.
- Oracle gap remains (learned post_mae=0.881 vs oracle=0.792): regret > 0, not solved.