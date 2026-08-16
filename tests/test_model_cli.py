from pathlib import Path

from typer.testing import CliRunner

from leakguard.cli import app
from leakguard.ml.candidate_v2_model_lifecycle import (
    CandidateV2ModelInstallError,
    CandidateV2ModelStatus,
)


runner = CliRunner()


def build_status(
    state,
    installed,
    verified,
    ready,
):
    return CandidateV2ModelStatus(
        artifact_path=Path(
            "candidate-v2.pkl"
        ),
        state=state,
        installed=installed,
        integrity_verified=verified,
        runtime_ready=ready,
        expected_sha256=(
            "a" * 64
        ),
        actual_sha256=(
            "a" * 64
            if installed
            else None
        ),
    )


def test_model_status_reports_verified(
    monkeypatch,
):
    monkeypatch.setattr(
        "leakguard.model_cli."
        "get_candidate_v2_model_status",
        lambda: build_status(
            "verified",
            True,
            True,
            True,
        ),
    )

    result = runner.invoke(
        app,
        [
            "model",
            "status",
        ],
    )

    assert result.exit_code == 0
    assert "installed" in result.stdout
    assert "verified" in result.stdout


def test_model_status_reports_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        "leakguard.model_cli."
        "get_candidate_v2_model_status",
        lambda: build_status(
            "missing",
            False,
            False,
            False,
        ),
    )

    result = runner.invoke(
        app,
        [
            "model",
            "status",
        ],
    )

    assert result.exit_code == 1
    assert "not installed" in result.stdout


def test_model_install_reports_refusal(
    tmp_path,
    monkeypatch,
):
    artifact = (
        tmp_path
        / "candidate.pkl"
    )

    artifact.write_bytes(
        b"fake"
    )

    def fail_install(
        source_path,
    ):
        raise CandidateV2ModelInstallError(
            "trusted SHA-256 verification failed"
        )

    monkeypatch.setattr(
        "leakguard.model_cli."
        "install_candidate_v2_artifact",
        fail_install,
    )

    result = runner.invoke(
        app,
        [
            "model",
            "install",
            str(
                artifact
            ),
        ],
    )

    assert result.exit_code == 2
    assert "refused" in result.stdout
