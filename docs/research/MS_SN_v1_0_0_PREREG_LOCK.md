# MS-SN v1.0.0 — Preregistration lock policy

MS-SN v1.0.0 configuration is **frozen** after PR #74 merges.
Any parameter mutation requires a new protocol version (for example: v1.0.1),
with a new config file and a new pinned digest.

`configs/ms_sn_v1_0_0.sha256` is the initial lock artifact for v1.0.0.
Runtime implementation must not silently mutate preregistered parameters.
v1.0.0 must not be edited after lock.
