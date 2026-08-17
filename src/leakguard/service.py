from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from leakguard.artifacts import scan_artifacts
from leakguard.config import (
    LeakGuardConfigError,
    load_leakguard_config,
    resolve_ml_advisory,
)
from leakguard.ml.candidate_v2_runtime import (
    CandidateV2RuntimeError,
    load_frozen_candidate_v2_runtime,
)
from leakguard.scanner import scan_path
from leakguard.staged import (
    GitStagedScanError,
    scan_staged_path,
)


ScanMode = Literal[
    "project",
    "staged",
]

GateState = Literal[
    "passed",
    "failed",
]


class ScanServiceError(Exception):
    """
    Base error for scan orchestration.
    """

    pass


class ProjectPathNotFoundError(
    ScanServiceError
):
    """
    Raised when the requested project
    directory does not exist.
    """

    pass


class ProjectPathTypeError(
    ScanServiceError
):
    """
    Raised when the requested project path
    is not a directory.
    """

    pass


class ScanConfigurationError(
    ScanServiceError
):
    """
    Raised when LeakGuard configuration or
    optional ML runtime cannot be used safely.
    """

    pass


class ScanExecutionError(
    ScanServiceError
):
    """
    Raised when a scan cannot be completed.
    """

    pass


@dataclass(frozen=True)
class ScanServiceResult:
    """
    Structured result shared by presentation
    layers such as the API and, later, CLI.
    """

    mode: ScanMode
    files_scanned: int
    findings: list[dict[str, Any]]
    ml_advisory_enabled: bool
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    @property
    def findings_count(self) -> int:
        return len(
            self.findings
        )

    @property
    def gate(self) -> GateState:
        if self.findings:
            return "failed"

        return "passed"


def resolve_project_root(
    root: Path,
) -> Path:
    """
    Normalize and validate the requested
    project directory.
    """

    project_root = (
        Path(root)
        .expanduser()
        .resolve()
    )

    if not project_root.exists():
        raise ProjectPathNotFoundError(
            "Project path does not exist."
        )

    if not project_root.is_dir():
        raise ProjectPathTypeError(
            "Project path must be a directory."
        )

    return project_root


def project_relative_display_path(
    file_path: str,
    root: Path,
) -> str:
    """
    Return project-relative API paths.

    Absolute host filesystem paths are not
    intentionally exposed in scan responses.
    """

    candidate = Path(
        file_path
    )

    if not candidate.is_absolute():
        return candidate.as_posix()

    try:
        return (
            candidate
            .relative_to(root)
            .as_posix()
        )

    except ValueError:
        # Scanner findings are expected to stay
        # inside the requested project. Fail
        # privacy-safe if that invariant changes.
        return candidate.name


def sanitize_ml_advisory(
    advisory: Any,
) -> dict[str, Any] | None:
    """
    Whitelist the Candidate v2 fields allowed
    to leave the scan engine.

    ML remains experimental and non-blocking.
    """

    if advisory is None:
        return None

    if not isinstance(
        advisory,
        dict,
    ):
        raise ScanExecutionError(
            "ML advisory returned an invalid "
            "structured result."
        )

    if advisory.get(
        "mode"
    ) != "advisory":
        raise ScanExecutionError(
            "ML advisory returned an invalid "
            "authority mode."
        )

    if advisory.get(
        "blocking"
    ) is not False:
        raise ScanExecutionError(
            "ML advisory returned an invalid "
            "blocking authority state."
        )

    if advisory.get(
        "calibrated"
    ) is not False:
        raise ScanExecutionError(
            "ML advisory returned an invalid "
            "calibration state."
        )

    return {
        "available": bool(
            advisory.get(
                "available",
                False,
            )
        ),
        "model": str(
            advisory.get(
                "model",
                "candidate-v2",
            )
        ),
        "mode": "advisory",
        "risk_score": float(
            advisory[
                "risk_score"
            ]
        ),
        "threshold": float(
            advisory[
                "threshold"
            ]
        ),
        "prediction": str(
            advisory[
                "prediction"
            ]
        ),
        "calibrated": False,
        "blocking": False,
    }


def sanitize_finding(
    finding: dict,
    root: Path,
) -> dict[str, Any]:
    """
    Create the explicit public representation
    of one finding.

    Unknown/internal finding fields are
    intentionally discarded.
    """

    candidate_score = (
        finding.get(
            "candidate_score"
        )
    )

    framework = finding.get(
        "framework"
    )

    reasons = finding.get(
        "reasons"
    ) or []

    return {
        "file": (
            project_relative_display_path(
                file_path=str(
                    finding[
                        "file"
                    ]
                ),
                root=root,
            )
        ),
        "line": int(
            finding[
                "line"
            ]
        ),
        "type": str(
            finding[
                "type"
            ]
        ),
        "severity": str(
            finding[
                "severity"
            ]
        ),
        "masked_value": str(
            finding[
                "masked_value"
            ]
        ),
        "candidate_score": (
            None
            if candidate_score is None
            else int(
                candidate_score
            )
        ),
        "framework": (
            None
            if framework is None
            else str(
                framework
            )
        ),
        "reasons": [
            str(reason)
            for reason in reasons
        ],
        "ml_advisory": (
            sanitize_ml_advisory(
                finding.get(
                    "ml_advisory"
                )
            )
        ),
    }


def run_security_scan(
    root: Path,
    *,
    staged: bool = False,
    ml_advisory_override: (
        bool | None
    ) = None,
) -> ScanServiceResult:
    """
    Run one LeakGuard security scan and return
    presentation-neutral structured data.

    Candidate v2 remains advisory only and
    cannot create independent blocking
    authority.
    """

    project_root = (
        resolve_project_root(
            root
        )
    )

    try:
        configuration = (
            load_leakguard_config(
                project_root
            )
        )

    except LeakGuardConfigError as error:
        raise ScanConfigurationError(
            "Invalid LeakGuard configuration."
        ) from error

    ml_advisory_enabled = (
        resolve_ml_advisory(
            cli_override=(
                ml_advisory_override
            ),
            config=configuration,
        )
    )

    ml_runtime = None

    if ml_advisory_enabled:
        try:
            ml_runtime = (
                load_frozen_candidate_v2_runtime()
            )

        except CandidateV2RuntimeError as error:
            raise ScanConfigurationError(
                "Candidate v2 advisory runtime "
                "is unavailable."
            ) from error

    try:
        if staged:
            files_scanned, findings = (
                scan_staged_path(
                    project_root,
                    ml_advisory_runtime=(
                        ml_runtime
                    ),
                )
            )

            mode: ScanMode = (
                "staged"
            )

        else:
            (
                source_files_scanned,
                source_findings,
            ) = scan_path(
                project_root,
                ml_advisory_runtime=(
                    ml_runtime
                ),
            )

            (
                artifact_files_scanned,
                artifact_findings,
            ) = scan_artifacts(
                project_root
            )

            files_scanned = (
                source_files_scanned
                + artifact_files_scanned
            )

            findings = (
                source_findings
                + artifact_findings
            )

            mode = "project"

    except GitStagedScanError as error:
        raise ScanExecutionError(
            "Unable to scan staged Git "
            "changes."
        ) from error

    public_findings = [
        sanitize_finding(
            finding=finding,
            root=project_root,
        )
        for finding in findings
    ]

    critical_count = sum(
        finding[
            "severity"
        ] == "CRITICAL"
        for finding in public_findings
    )

    high_count = sum(
        finding[
            "severity"
        ] == "HIGH"
        for finding in public_findings
    )

    medium_count = sum(
        finding[
            "severity"
        ] == "MEDIUM"
        for finding in public_findings
    )

    low_count = sum(
        finding[
            "severity"
        ] == "LOW"
        for finding in public_findings
    )

    return ScanServiceResult(
        mode=mode,
        files_scanned=files_scanned,
        findings=public_findings,
        ml_advisory_enabled=(
            ml_advisory_enabled
        ),
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
    )
