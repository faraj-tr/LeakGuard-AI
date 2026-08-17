from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal


ML_POLICY_CHOICES = (
    "Use project configuration",
    "Enable Candidate v2 advisory",
    "Disable Candidate v2 advisory",
)


class DashboardPayloadError(Exception):
    """
    Raised when an API response cannot be
    represented safely by the dashboard.
    """

    pass


@dataclass(frozen=True)
class MLAdvisoryView:
    available: bool
    model: str
    risk_score: float
    threshold: float
    prediction: Literal[
        "suspicious",
        "lower_risk",
    ]
    calibrated: bool
    blocking: bool


@dataclass(frozen=True)
class FindingView:
    file: str
    line: int
    finding_type: str
    severity: Literal[
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]
    masked_value: str
    candidate_score: int | None
    framework: str | None
    reasons: tuple[str, ...]
    ml_advisory: MLAdvisoryView | None


@dataclass(frozen=True)
class SeverityView:
    critical: int
    high: int
    medium: int
    low: int


@dataclass(frozen=True)
class ScanView:
    mode: Literal[
        "project",
        "staged",
    ]
    files_scanned: int
    findings_count: int
    gate: Literal[
        "passed",
        "failed",
    ]
    ml_advisory_enabled: bool
    severity: SeverityView
    findings: tuple[
        FindingView,
        ...
    ]


def resolve_ml_override(
    choice: str,
) -> bool | None:
    """
    Convert the dashboard's three-state ML
    policy control to the public API contract.
    """

    if choice == (
        "Use project configuration"
    ):
        return None

    if choice == (
        "Enable Candidate v2 advisory"
    ):
        return True

    if choice == (
        "Disable Candidate v2 advisory"
    ):
        return False

    raise ValueError(
        "Unsupported ML policy choice."
    )


def require_nonnegative_int(
    value: Any,
    *,
    field_name: str,
) -> int:
    if (
        type(value) is not int
        or value < 0
    ):
        raise DashboardPayloadError(
            f"Invalid {field_name}."
        )

    return value


def require_text(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise DashboardPayloadError(
            f"Invalid {field_name}."
        )

    return value


def build_ml_advisory_view(
    value: Any,
) -> MLAdvisoryView | None:
    """
    Accept only the known non-blocking
    Candidate v2 advisory contract.
    """

    if value is None:
        return None

    if not isinstance(
        value,
        Mapping,
    ):
        raise DashboardPayloadError(
            "Invalid ML advisory."
        )

    if value.get(
        "mode"
    ) != "advisory":
        raise DashboardPayloadError(
            "Invalid ML advisory mode."
        )

    if value.get(
        "calibrated"
    ) is not False:
        raise DashboardPayloadError(
            "Invalid ML calibration state."
        )

    if value.get(
        "blocking"
    ) is not False:
        raise DashboardPayloadError(
            "Invalid ML blocking authority."
        )

    if type(
        value.get(
            "available"
        )
    ) is not bool:
        raise DashboardPayloadError(
            "Invalid ML availability state."
        )

    prediction = value.get(
        "prediction"
    )

    if prediction not in {
        "suspicious",
        "lower_risk",
    }:
        raise DashboardPayloadError(
            "Invalid ML prediction."
        )

    risk_score = value.get(
        "risk_score"
    )

    threshold = value.get(
        "threshold"
    )

    if (
        isinstance(
            risk_score,
            bool,
        )
        or not isinstance(
            risk_score,
            (int, float),
        )
    ):
        raise DashboardPayloadError(
            "Invalid ML risk score."
        )

    if (
        isinstance(
            threshold,
            bool,
        )
        or not isinstance(
            threshold,
            (int, float),
        )
    ):
        raise DashboardPayloadError(
            "Invalid ML threshold."
        )

    risk_score = float(
        risk_score
    )

    threshold = float(
        threshold
    )

    if not (
        0.0
        <= risk_score
        <= 1.0
    ):
        raise DashboardPayloadError(
            "Invalid ML risk score."
        )

    if not (
        0.0
        <= threshold
        <= 1.0
    ):
        raise DashboardPayloadError(
            "Invalid ML threshold."
        )

    model = require_text(
        value.get(
            "model"
        ),
        field_name="ML model",
    )

    return MLAdvisoryView(
        available=value[
            "available"
        ],
        model=model,
        risk_score=risk_score,
        threshold=threshold,
        prediction=prediction,
        calibrated=False,
        blocking=False,
    )


def build_finding_view(
    value: Any,
) -> FindingView:
    """
    Whitelist the finding fields that the UI
    is allowed to render.
    """

    if not isinstance(
        value,
        Mapping,
    ):
        raise DashboardPayloadError(
            "Invalid finding."
        )

    severity = value.get(
        "severity"
    )

    if severity not in {
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
    }:
        raise DashboardPayloadError(
            "Invalid finding severity."
        )

    line = value.get(
        "line"
    )

    if (
        type(line) is not int
        or line < 0
    ):
        raise DashboardPayloadError(
            "Invalid finding line."
        )

    candidate_score = (
        value.get(
            "candidate_score"
        )
    )

    if (
        candidate_score is not None
        and type(
            candidate_score
        ) is not int
    ):
        raise DashboardPayloadError(
            "Invalid candidate score."
        )

    framework = value.get(
        "framework"
    )

    if (
        framework is not None
        and not isinstance(
            framework,
            str,
        )
    ):
        raise DashboardPayloadError(
            "Invalid finding framework."
        )

    reasons = value.get(
        "reasons"
    )

    if not isinstance(
        reasons,
        list,
    ):
        raise DashboardPayloadError(
            "Invalid finding reasons."
        )

    if not all(
        isinstance(
            reason,
            str,
        )
        for reason in reasons
    ):
        raise DashboardPayloadError(
            "Invalid finding reason."
        )

    return FindingView(
        file=require_text(
            value.get(
                "file"
            ),
            field_name="finding file",
        ),
        line=line,
        finding_type=require_text(
            value.get(
                "type"
            ),
            field_name="finding type",
        ),
        severity=severity,
        masked_value=require_text(
            value.get(
                "masked_value"
            ),
            field_name=(
                "masked finding value"
            ),
        ),
        candidate_score=(
            candidate_score
        ),
        framework=framework,
        reasons=tuple(
            reasons
        ),
        ml_advisory=(
            build_ml_advisory_view(
                value.get(
                    "ml_advisory"
                )
            )
        ),
    )


def build_scan_view(
    payload: Any,
) -> ScanView:
    """
    Convert a public /v1/scan response into a
    strict dashboard view model.

    Unknown response fields are discarded.
    Inconsistent gate or count information is
    rejected rather than rendered.
    """

    if not isinstance(
        payload,
        Mapping,
    ):
        raise DashboardPayloadError(
            "Invalid scan response."
        )

    mode = payload.get(
        "mode"
    )

    if mode not in {
        "project",
        "staged",
    }:
        raise DashboardPayloadError(
            "Invalid scan mode."
        )

    gate = payload.get(
        "gate"
    )

    if gate not in {
        "passed",
        "failed",
    }:
        raise DashboardPayloadError(
            "Invalid gate state."
        )

    ml_enabled = payload.get(
        "ml_advisory_enabled"
    )

    if type(
        ml_enabled
    ) is not bool:
        raise DashboardPayloadError(
            "Invalid ML enabled state."
        )

    files_scanned = (
        require_nonnegative_int(
            payload.get(
                "files_scanned"
            ),
            field_name="files scanned",
        )
    )

    findings_count = (
        require_nonnegative_int(
            payload.get(
                "findings_count"
            ),
            field_name="findings count",
        )
    )

    severity_payload = (
        payload.get(
            "severity_counts"
        )
    )

    if not isinstance(
        severity_payload,
        Mapping,
    ):
        raise DashboardPayloadError(
            "Invalid severity counts."
        )

    severity = SeverityView(
        critical=require_nonnegative_int(
            severity_payload.get(
                "critical"
            ),
            field_name="critical count",
        ),
        high=require_nonnegative_int(
            severity_payload.get(
                "high"
            ),
            field_name="high count",
        ),
        medium=require_nonnegative_int(
            severity_payload.get(
                "medium"
            ),
            field_name="medium count",
        ),
        low=require_nonnegative_int(
            severity_payload.get(
                "low"
            ),
            field_name="low count",
        ),
    )

    findings_payload = payload.get(
        "findings"
    )

    if not isinstance(
        findings_payload,
        list,
    ):
        raise DashboardPayloadError(
            "Invalid findings collection."
        )

    findings = tuple(
        build_finding_view(
            finding
        )
        for finding in findings_payload
    )

    if findings_count != len(
        findings
    ):
        raise DashboardPayloadError(
            "Finding count does not match "
            "the findings collection."
        )

    severity_total = (
        severity.critical
        + severity.high
        + severity.medium
        + severity.low
    )

    if severity_total != (
        findings_count
    ):
        raise DashboardPayloadError(
            "Severity counts do not match "
            "the finding count."
        )

    expected_gate = (
        "failed"
        if findings_count
        else "passed"
    )

    if gate != expected_gate:
        raise DashboardPayloadError(
            "Gate state is inconsistent "
            "with findings."
        )

    return ScanView(
        mode=mode,
        files_scanned=(
            files_scanned
        ),
        findings_count=(
            findings_count
        ),
        gate=gate,
        ml_advisory_enabled=(
            ml_enabled
        ),
        severity=severity,
        findings=findings,
    )
