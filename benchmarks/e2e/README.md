# LeakGuard End-to-End Security Gate Benchmark v1

## Purpose

This benchmark measures LeakGuard as an end-to-end security gate rather than
measuring Candidate v2 in isolation.

It is intentionally separate from the Candidate v2 development, dev-set, and
independent holdout evaluation pipeline.

## What is measured

The benchmark reports two headline results.

### Secret-detection classification

Coverage-only cases are excluded.

For each isolated case:

- expected secret exposure + at least one finding = true positive
- expected safe case + zero findings = true negative
- expected safe case + one or more findings = false positive
- expected secret exposure + zero findings = false negative

The report calculates:

- accuracy
- precision
- recall
- F1
- false-positive rate
- false-negative rate
- confusion matrix

### Whole security-gate behavior

This includes secret cases, safe controls, and fail-closed scan-coverage cases.

A case is correct when LeakGuard's PASS/FAIL gate matches the benchmark's
expected gate state.

## Corpus design

v1 contains 340 isolated cases:

- 160 synthetic secret-exposure cases
- 160 safe-control cases
- 20 fail-closed coverage-safety cases

Positive families cover:

- hardcoded passwords
- API keys
- bearer tokens
- database credentials
- client-side environment exposure
- generic secret candidates
- artifact propagation
- staged Git secrets

Safe-control families include matched benign variants and deliberately difficult
high-entropy identifiers to expose false-positive behavior rather than hiding it.

Coverage-safety cases include oversized supported files and binary evidence in
supported text formats.

## Safety

All credential-like fixture values are synthetic and intentionally fake.

The benchmark does not validate any credential against an external provider.

Fixture values are created only in temporary directories during execution.

The JSON report never stores raw fixture values.

## Candidate v2

Candidate v2 is disabled for gate benchmarking.

This is intentional: Candidate v2 is advisory-only and cannot create, suppress,
escalate, pass, or fail a security finding. Enabling it cannot change the gate
confusion matrix.

Candidate v2's independent holdout metrics must therefore remain a separate
reported result.

## Interpretation

This benchmark produces an **internal synthetic end-to-end benchmark**, not a
claim of universal real-world detection accuracy.

The benchmark should be frozen before its results are used for tuning. If the
implementation is changed based on benchmark failures, create a new benchmark
version or preserve v1 as a post-selection evaluation record.

A future external evaluation should use an independently maintained corpus or a
safely sanitized external benchmark compatible with LeakGuard's supported file
scope.
