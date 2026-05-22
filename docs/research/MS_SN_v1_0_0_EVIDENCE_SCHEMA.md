# MS-SN v1.0.0 — Evidence schema

## PR #74 status

PR #74 is scaffold-only. Runtime validation evidence is out of scope.

## Scaffold manifest

Canonical path:

`evidence/ms_sn_v1_0_0/manifest.json`

Required fields:
- `protocol`
- `pr`
- `status`
- `claim_boundary`
- `config_sha256`
- `runs`

Required values:
- `protocol = "MS-SN-v1.0.0"`
- `pr = 74`
- `status = "SCAFFOLD_ONLY"`

Allowed scaffold verdicts:
- `INVALID_RUN`
- `RED_EXPECTED`
- `RED_UNEXPECTED`
- `GREEN`

`INVALID_RUN` is allowed only for scaffold placeholders and must not be interpreted as runtime evidence.

## Runtime manifest

Canonical future path:

`evidence/ms_sn_v1_0_0/runtime_manifest.json`

Runtime manifest is not required for PR #74.

If present in a future PR, it must include:
- `status = "RUNTIME_VALIDATED"`
- `head_sha`
- non-empty `hashes`
- non-empty `tests`
- `artifact_sha256` or `runtime_artifact_sha256`
- no `INVALID_RUN` verdicts
