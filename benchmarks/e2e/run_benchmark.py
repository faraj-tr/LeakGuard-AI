from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from leakguard.service import (
    ScanServiceError,
    run_security_scan,
)


BENCHMARK_NAME = "LeakGuard End-to-End Security Gate Benchmark"
BENCHMARK_VERSION = "v1"
CASES_PER_CATEGORY = 20
DEFAULT_REPORT_PATH = Path("reports/e2e_gate_benchmark_v1.json")


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    family: str
    track: str
    expected_gate: str
    expected_type: str | None
    setup: Callable[[Path, int], None]


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    family: str
    track: str
    expected_gate: str
    predicted_gate: str
    expected_type: str | None
    expected_type_found: bool | None
    findings_count: int
    finding_types: tuple[str, ...]
    correct_gate: bool


def _write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _write_bytes(root: Path, relative_path: str, content: bytes) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _fake_value(prefix: str, index: int, width: int = 24) -> str:
    suffix = f"{index:04d}"
    body = (f"Aa9{index:04d}Xy7Qp3Lm8Nz2" * 4)[:width]
    return f"LG_BENCH_FAKE_{prefix}_{suffix}_{body}"


def _init_git_repo(root: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def _stage_all(root: Path) -> None:
    subprocess.run(
        ["git", "add", "-A"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


# ---------------------------------------------------------------------------
# Positive secret-exposure cases
# ---------------------------------------------------------------------------


def setup_password_positive(root: Path, index: int) -> None:
    value = _fake_value("PASSWORD", index)
    if index % 2 == 0:
        _write_text(
            root,
            "config.py",
            f'service_password = "{value}"\n',
        )
    else:
        _write_text(
            root,
            "settings.js",
            f'const db_password = "{value}";\n',
        )


def setup_api_key_positive(root: Path, index: int) -> None:
    value = _fake_value("APIKEY", index)
    if index % 2 == 0:
        _write_text(
            root,
            "client.ts",
            f'const api_key = "{value}";\n',
        )
    else:
        _write_text(
            root,
            "settings.yaml",
            f'api_key: "{value}"\n',
        )


def setup_bearer_positive(root: Path, index: int) -> None:
    token = _fake_value("BEARER", index).replace("_", "")
    _write_text(
        root,
        "headers.py",
        f'AUTH_HEADER = "Bearer {token}"\n',
    )


def setup_database_positive(root: Path, index: int) -> None:
    password = _fake_value("DB", index).replace("@", "")
    _write_text(
        root,
        "database.py",
        (
            'DATABASE_URL = "postgresql://bench_user:'
            f'{password}@localhost:5432/app"\n'
        ),
    )


def setup_client_exposure_positive(root: Path, index: int) -> None:
    value = _fake_value("CLIENT", index)
    variable = "VITE_API_KEY" if index % 2 == 0 else "NEXT_PUBLIC_CLIENT_SECRET"
    _write_text(
        root,
        ".env",
        f"{variable}={value}\n",
    )


def setup_generic_positive(root: Path, index: int) -> None:
    value = _fake_value("GENERIC", index)
    variable = "session_credential" if index % 2 == 0 else "service_secret"
    _write_text(
        root,
        "runtime.py",
        f'{variable} = "{value}"\n',
    )


def setup_artifact_positive(root: Path, index: int) -> None:
    value = _fake_value("ARTIFACT", index)
    _write_text(
        root,
        ".env",
        f"SERVER_SECRET={value}\n",
    )
    artifact_root = "dist" if index % 2 == 0 else "build"
    _write_text(
        root,
        f"{artifact_root}/assets/app.js",
        f'window.__BOOTSTRAP__ = "{value}";\n',
    )


def setup_staged_positive(root: Path, index: int) -> None:
    _init_git_repo(root)
    value = _fake_value("STAGED", index)
    _write_text(
        root,
        "config.py",
        f'auth_token = "{value}"\n',
    )
    _stage_all(root)


# ---------------------------------------------------------------------------
# Negative / safe-control cases
# ---------------------------------------------------------------------------


def setup_password_expression_safe(root: Path, index: int) -> None:
    _write_text(
        root,
        "config.py",
        'password = os.getenv("PASSWORD")\n',
    )


def setup_api_expression_safe(root: Path, index: int) -> None:
    _write_text(
        root,
        "settings.ts",
        "const api_key = config.apiKey;\n",
    )


def setup_bearer_text_safe(root: Path, index: int) -> None:
    _write_text(
        root,
        "ui.py",
        'MESSAGE = "Use a bearer token from your secret manager"\n',
    )


def setup_database_url_safe(root: Path, index: int) -> None:
    _write_text(
        root,
        "database.py",
        'DATABASE_URL = "sqlite:///app.db"\n',
    )


def setup_client_public_safe(root: Path, index: int) -> None:
    variable = "VITE_APP_NAME" if index % 2 == 0 else "NEXT_PUBLIC_SITE_LABEL"
    _write_text(
        root,
        ".env",
        f"{variable}=LeakGuard\n",
    )


def setup_benign_high_entropy_safe(root: Path, index: int) -> None:
    # Deliberately difficult negative:
    # a long, compact identifier that is not a credential.
    value = f"asset-{index:04d}-A9f3D7k2M8q4Z1x6C5v0"
    variable = "asset_id" if index % 2 == 0 else "cache_key_name"
    _write_text(
        root,
        "metadata.py",
        f'{variable} = "{value}"\n',
    )


def setup_artifact_nonpropagation_safe(root: Path, index: int) -> None:
    value = _fake_value("LOCAL_ONLY", index)
    _write_text(
        root,
        ".env",
        f"SERVER_SECRET={value}\n",
    )
    _write_text(
        root,
        "dist/assets/app.js",
        'window.__BOOTSTRAP__ = "public-build-value";\n',
    )


def setup_staged_safe(root: Path, index: int) -> None:
    _init_git_repo(root)
    _write_text(
        root,
        "config.py",
        'APP_NAME = "LeakGuard Benchmark"\n',
    )
    _stage_all(root)


# ---------------------------------------------------------------------------
# Coverage-safety / fail-closed cases
# ---------------------------------------------------------------------------


def setup_oversized_coverage(root: Path, index: int) -> None:
    # Slightly above the current 2 MiB safety limit.
    payload = b"A" * ((2 * 1024 * 1024) + 64)
    _write_bytes(
        root,
        "oversized.py",
        payload,
    )


def setup_binary_coverage(root: Path, index: int) -> None:
    _write_bytes(
        root,
        "binary.json",
        b'{"name":"safe"}\x00\x01\x02',
    )


def build_cases() -> list[BenchmarkCase]:
    positive_specs = [
        ("hardcoded_password", "project", "Hardcoded Password", setup_password_positive),
        ("api_key", "project", "API Key", setup_api_key_positive),
        ("bearer_token", "project", "Bearer Token", setup_bearer_positive),
        ("database_credential", "project", "Database Credential", setup_database_positive),
        (
            "client_side_exposure",
            "project",
            "Client-Side Secret Exposure",
            setup_client_exposure_positive,
        ),
        (
            "generic_secret_candidate",
            "project",
            "Unknown Secret Candidate",
            setup_generic_positive,
        ),
        (
            "artifact_propagation",
            "project",
            "Artifact Secret Exposure",
            setup_artifact_positive,
        ),
        ("staged_secret", "staged", None, setup_staged_positive),
    ]

    negative_specs = [
        ("safe_password_expression", "project", setup_password_expression_safe),
        ("safe_api_expression", "project", setup_api_expression_safe),
        ("safe_bearer_text", "project", setup_bearer_text_safe),
        ("safe_database_url", "project", setup_database_url_safe),
        ("safe_client_public", "project", setup_client_public_safe),
        ("safe_high_entropy_identifier", "project", setup_benign_high_entropy_safe),
        ("safe_artifact_nonpropagation", "project", setup_artifact_nonpropagation_safe),
        ("safe_staged_change", "staged", setup_staged_safe),
    ]

    coverage_specs = [
        ("coverage_oversized_file", setup_oversized_coverage),
        ("coverage_binary_content", setup_binary_coverage),
    ]

    cases: list[BenchmarkCase] = []

    for family, track, expected_type, setup in positive_specs:
        for index in range(CASES_PER_CATEGORY):
            cases.append(
                BenchmarkCase(
                    case_id=f"{family}-{index:03d}",
                    family=family,
                    track=track,
                    expected_gate="failed",
                    expected_type=expected_type,
                    setup=setup,
                )
            )

    for family, track, setup in negative_specs:
        for index in range(CASES_PER_CATEGORY):
            cases.append(
                BenchmarkCase(
                    case_id=f"{family}-{index:03d}",
                    family=family,
                    track=track,
                    expected_gate="passed",
                    expected_type=None,
                    setup=setup,
                )
            )

    # Coverage cases intentionally fail closed. They are included in the
    # overall gate-behavior score, but excluded from secret-classification
    # precision/recall because they are not themselves secret exposures.
    for family, setup in coverage_specs:
        for index in range(CASES_PER_CATEGORY // 2):
            cases.append(
                BenchmarkCase(
                    case_id=f"{family}-{index:03d}",
                    family=family,
                    track="coverage",
                    expected_gate="failed",
                    expected_type="Scan Coverage Limitation",
                    setup=setup,
                )
            )

    return cases


def corpus_digest(cases: list[BenchmarkCase]) -> str:
    hasher = hashlib.sha256()

    for case in cases:
        with tempfile.TemporaryDirectory(prefix="leakguard-e2e-hash-") as tmp:
            root = Path(tmp)
            case.setup(root, int(case.case_id.rsplit("-", 1)[1]))

            hasher.update(case.case_id.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(case.family.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(case.track.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(case.expected_gate.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update((case.expected_type or "").encode("utf-8"))
            hasher.update(b"\0")

            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue

                relative = path.relative_to(root).as_posix()

                # Git internals are an implementation detail of staged-case
                # setup and are intentionally excluded from corpus identity.
                if relative == ".git" or relative.startswith(".git/"):
                    continue

                hasher.update(relative.encode("utf-8"))
                hasher.update(b"\0")
                hasher.update(hashlib.sha256(path.read_bytes()).digest())

    return hasher.hexdigest()


def execute_case(case: BenchmarkCase) -> CaseResult:
    with tempfile.TemporaryDirectory(prefix="leakguard-e2e-") as tmp:
        root = Path(tmp)

        index = int(case.case_id.rsplit("-", 1)[1])
        case.setup(root, index)

        staged = case.track == "staged"

        try:
            result = run_security_scan(
                root,
                staged=staged,
                ml_advisory_override=False,
            )
        except ScanServiceError as error:
            raise RuntimeError(
                f"Benchmark case {case.case_id} could not be executed safely."
            ) from error

        finding_types = tuple(
            finding["type"]
            for finding in result.findings
        )

        expected_type_found: bool | None
        if case.expected_type is None:
            expected_type_found = None
        else:
            expected_type_found = case.expected_type in finding_types

        return CaseResult(
            case_id=case.case_id,
            family=case.family,
            track=case.track,
            expected_gate=case.expected_gate,
            predicted_gate=result.gate,
            expected_type=case.expected_type,
            expected_type_found=expected_type_found,
            findings_count=result.findings_count,
            finding_types=finding_types,
            correct_gate=result.gate == case.expected_gate,
        )


def _safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def compute_metrics(results: list[CaseResult]) -> dict:
    # Secret-classification metrics exclude coverage-only fail-closed cases.
    secret_results = [
        result
        for result in results
        if result.track != "coverage"
    ]

    tp = sum(
        result.expected_gate == "failed"
        and result.predicted_gate == "failed"
        for result in secret_results
    )
    tn = sum(
        result.expected_gate == "passed"
        and result.predicted_gate == "passed"
        for result in secret_results
    )
    fp = sum(
        result.expected_gate == "passed"
        and result.predicted_gate == "failed"
        for result in secret_results
    )
    fn = sum(
        result.expected_gate == "failed"
        and result.predicted_gate == "passed"
        for result in secret_results
    )

    accuracy = _safe_divide(tp + tn, tp + tn + fp + fn)
    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    f1 = _safe_divide(2 * precision * recall, precision + recall)
    false_positive_rate = _safe_divide(fp, fp + tn)
    false_negative_rate = _safe_divide(fn, fn + tp)

    gate_correct = sum(result.correct_gate for result in results)
    gate_accuracy = _safe_divide(gate_correct, len(results))

    family_totals = Counter(result.family for result in results)
    family_gate_correct = Counter(
        result.family
        for result in results
        if result.correct_gate
    )

    expected_type_totals = Counter()
    expected_type_hits = Counter()

    for result in results:
        if result.expected_type is None:
            continue
        expected_type_totals[result.family] += 1
        if result.expected_type_found:
            expected_type_hits[result.family] += 1

    per_family = {}
    for family in sorted(family_totals):
        per_family[family] = {
            "cases": family_totals[family],
            "gate_accuracy": _safe_divide(
                family_gate_correct[family],
                family_totals[family],
            ),
        }

        if expected_type_totals[family]:
            per_family[family]["expected_type_recall"] = _safe_divide(
                expected_type_hits[family],
                expected_type_totals[family],
            )

    false_positive_families = Counter(
        result.family
        for result in secret_results
        if result.expected_gate == "passed"
        and result.predicted_gate == "failed"
    )

    false_negative_families = Counter(
        result.family
        for result in secret_results
        if result.expected_gate == "failed"
        and result.predicted_gate == "passed"
    )

    return {
        "secret_detection": {
            "cases": len(secret_results),
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "false_positive_rate": false_positive_rate,
            "false_negative_rate": false_negative_rate,
        },
        "security_gate": {
            "cases": len(results),
            "correct": gate_correct,
            "incorrect": len(results) - gate_correct,
            "accuracy": gate_accuracy,
        },
        "false_positive_families": dict(sorted(false_positive_families.items())),
        "false_negative_families": dict(sorted(false_negative_families.items())),
        "per_family": per_family,
    }


def build_public_case_results(results: list[CaseResult]) -> list[dict]:
    # Deliberately contains no raw benchmark fixture values.
    return [
        {
            "case_id": result.case_id,
            "family": result.family,
            "track": result.track,
            "expected_gate": result.expected_gate,
            "predicted_gate": result.predicted_gate,
            "expected_type": result.expected_type,
            "expected_type_found": result.expected_type_found,
            "findings_count": result.findings_count,
            "finding_types": list(result.finding_types),
            "correct_gate": result.correct_gate,
        }
        for result in results
    ]


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def print_summary(metrics: dict, digest: str, total_cases: int) -> None:
    secret = metrics["secret_detection"]
    gate = metrics["security_gate"]

    print()
    print("=" * 68)
    print(f"{BENCHMARK_NAME} {BENCHMARK_VERSION}")
    print("=" * 68)
    print(f"Corpus SHA-256: {digest}")
    print(f"Total gate cases: {total_cases}")
    print()
    print("Secret-detection classification")
    print("-" * 68)
    print(f"Cases:                {secret['cases']}")
    print(f"Accuracy:             {format_percent(secret['accuracy'])}")
    print(f"Precision:            {format_percent(secret['precision'])}")
    print(f"Recall:               {format_percent(secret['recall'])}")
    print(f"F1:                   {format_percent(secret['f1'])}")
    print(f"False-positive rate:  {format_percent(secret['false_positive_rate'])}")
    print(f"False-negative rate:  {format_percent(secret['false_negative_rate'])}")
    print(
        "Confusion matrix:      "
        f"TP={secret['true_positive']} "
        f"TN={secret['true_negative']} "
        f"FP={secret['false_positive']} "
        f"FN={secret['false_negative']}"
    )
    print()
    print("Whole security-gate behavior")
    print("-" * 68)
    print(f"Cases:                {gate['cases']}")
    print(f"Accuracy:             {format_percent(gate['accuracy'])}")
    print(f"Correct:              {gate['correct']}")
    print(f"Incorrect:            {gate['incorrect']}")
    print()
    print("Important:")
    print(
        "Candidate v2 ML is intentionally disabled in this benchmark because "
        "it has no blocking authority and therefore cannot change PASS/FAIL."
    )
    print(
        "Its independent holdout metrics must be reported separately from "
        "these end-to-end gate metrics."
    )
    print("=" * 68)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run LeakGuard's locked synthetic end-to-end security-gate "
            "benchmark without exposing raw fixture values in the report."
        )
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="JSON report path.",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Run the benchmark without writing a JSON report.",
    )
    args = parser.parse_args()

    cases = build_cases()
    digest = corpus_digest(cases)

    results: list[CaseResult] = []

    for position, case in enumerate(cases, start=1):
        result = execute_case(case)
        results.append(result)

        if position % 25 == 0 or position == len(cases):
            print(f"Executed {position}/{len(cases)} cases...")

    metrics = compute_metrics(results)

    print_summary(
        metrics=metrics,
        digest=digest,
        total_cases=len(cases),
    )

    if not args.no_report:
        report_path = args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "benchmark": BENCHMARK_NAME,
            "benchmark_version": BENCHMARK_VERSION,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "corpus_sha256": digest,
            "cases_per_category": CASES_PER_CATEGORY,
            "ml_advisory_enabled": False,
            "ml_authority_note": (
                "Candidate v2 is advisory-only and cannot change gate state; "
                "its independent holdout metrics are reported separately."
            ),
            "metrics": metrics,
            "cases": build_public_case_results(results),
        }

        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        print(f"Report written to: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
