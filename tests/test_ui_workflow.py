import pytest

from leakguard.ui.workflow import (
    DashboardPayloadError,
    build_scan_view,
    resolve_ml_override,
)


def build_valid_payload():
    return {
        "mode": "project",
        "files_scanned": 2,
        "findings_count": 1,
        "gate": "failed",
        "ml_advisory_enabled": False,
        "severity_counts": {
            "critical": 0,
            "high": 1,
            "medium": 0,
            "low": 0,
        },
        "findings": [
            {
                "file": "config.py",
                "line": 4,
                "type": (
                    "Hardcoded Password"
                ),
                "severity": "HIGH",
                "masked_value": (
                    "LEAK*********C123"
                ),
                "candidate_score": None,
                "framework": None,
                "reasons": [
                    "Known secret pattern"
                ],
                "ml_advisory": None,
            }
        ],
    }


def test_ml_policy_uses_project_configuration():
    assert (
        resolve_ml_override(
            "Use project configuration"
        )
        is None
    )


def test_ml_policy_can_force_enable():
    assert (
        resolve_ml_override(
            "Enable Candidate v2 advisory"
        )
        is True
    )


def test_ml_policy_can_force_disable():
    assert (
        resolve_ml_override(
            "Disable Candidate v2 advisory"
        )
        is False
    )


def test_scan_view_whitelists_public_fields():
    payload = build_valid_payload()

    payload[
        "server_internal"
    ] = "do-not-render"

    payload[
        "findings"
    ][0][
        "raw_value"
    ] = (
        "LEAKGUARD_FAKE_RAW_SECRET_123"
    )

    view = build_scan_view(
        payload
    )

    assert view.mode == "project"
    assert view.gate == "failed"
    assert view.files_scanned == 2
    assert view.findings_count == 1

    finding = view.findings[0]

    assert (
        finding.finding_type
        == "Hardcoded Password"
    )

    assert (
        finding.masked_value
        == "LEAK*********C123"
    )

    assert not hasattr(
        finding,
        "raw_value",
    )

    assert not hasattr(
        view,
        "server_internal",
    )


def test_scan_view_rejects_inconsistent_gate():
    payload = build_valid_payload()

    payload[
        "gate"
    ] = "passed"

    with pytest.raises(
        DashboardPayloadError,
        match=(
            "Gate state is inconsistent"
        ),
    ):
        build_scan_view(
            payload
        )
