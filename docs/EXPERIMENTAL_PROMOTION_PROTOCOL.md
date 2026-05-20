# Experimental Promotion Protocol

## Purpose

This protocol prevents experimental code from accidentally becoming canonical.

A directory named `experimental` is not a license to bypass evidence, provenance, or claim boundaries. It is a quarantine lane for candidate mechanisms that may be explored without changing the accepted mainline contract.

## Scope

Applies to:

```text
src/ctios/experimental/**
```

Current known candidate:

```text
ctios.experimental.neural_attention_adapter
ctios.experimental.neural_attention_runner
```

## Status classes

```text
experimental_candidate
contract_checked
preregistered
sandbox_evaluated
promotion_candidate
canonical
rejected
negative_result
```

## Required before contract_checked

- module imports without side effects
- deterministic replay check
- finite predictions/errors/uncertainty
- invalid stream rejection
- bounded history behavior
- runner returns stable metric keys
- no hidden schedule inputs
- no replacement of canonical v9 path

## Required before preregistered

A preregistration file must define:

- task
- baseline
- metric
- dataset or synthetic stream generator
- pass condition
- fail condition
- negative-result acceptance rule
- claim boundary

## Required before sandbox_evaluated

- isolated branch
- reproducible command
- clean test environment
- captured logs
- captured metrics
- no protected branch writes

## Required before promotion_candidate

- canonical tests
- scalar baseline comparison
- no-leakage check
- deterministic replay check
- README claim boundary unchanged or explicitly updated with evidence
- provenance policy decision recorded
- rollback path documented

## Promotion decision

Promotion to canonical requires:

```text
no hard-blocking gate
AND deterministic replay
AND baseline comparison complete
AND claim boundary explicit
AND rollback trivial
AND operator approval for public-facing claim changes
```

## Forbidden shortcuts

Forbidden:

- importing from `experimental` in canonical runners without a promotion PR
- changing README capability claims based on experimental presence
- using experimental metrics as release evidence before preregistration
- including experimental files in provenance root without stating the policy
- letting the same agent generate and approve the promotion

## Negative-result rule

If the candidate fails to beat baseline under preregistered metrics, preserve it as a negative result when it teaches one of:

- no headroom
- leakage risk
- instability
- carrier sensitivity
- boundary mismatch
- complexity without gain

Failure is not deletion by default.

Failure becomes memory.
