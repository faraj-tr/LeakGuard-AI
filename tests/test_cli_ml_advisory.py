from typer.testing import CliRunner

from leakguard.cli import app


runner = CliRunner()


class StubRuntime:

    def score(
        self,
        variable_name,
        value,
    ):
        return {
            "available": True,
            "model": "candidate-v2",
            "mode": "advisory",
            "risk_score": 0.8734,
            "threshold": 0.50,
            "prediction": "suspicious",
            "calibrated": False,
            "blocking": False,
        }


def test_cli_ml_advisory_flag_loads_runtime_once(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "mystery.py"
    )

    secret = (
        "K7mP2xQ9vL4sN8zA1c"
    )

    test_file.write_text(
        f'x = "{secret}"',
        encoding="utf-8",
    )

    calls = []

    def fake_loader():
        calls.append(
            True
        )

        return StubRuntime()

    monkeypatch.setattr(
        "leakguard.cli."
        "load_frozen_candidate_v2_runtime",
        fake_loader,
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--ml-advisory",
        ],
    )

    assert result.exit_code == 1

    assert len(
        calls
    ) == 1

    assert (
        "ML Advisory"
        in result.stdout
    )

    assert (
        "87.3%"
        in result.stdout
    )

    assert (
        "non-blocking"
        in result.stdout
    )

    assert secret not in (
        result.stdout
    )


def test_cli_without_flag_does_not_load_ml_runtime(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "app.py"
    )

    test_file.write_text(
        'message = "Hello world"',
        encoding="utf-8",
    )

    def forbidden_loader():
        raise AssertionError(
            "ML runtime must not load "
            "without --ml-advisory."
        )

    monkeypatch.setattr(
        "leakguard.cli."
        "load_frozen_candidate_v2_runtime",
        forbidden_loader,
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0

    assert (
        "Security scan passed"
        in result.stdout
    )


def test_cli_reports_missing_ml_artifact_cleanly(
    tmp_path,
    monkeypatch,
):
    from leakguard.ml.candidate_v2_runtime import (
        CandidateV2RuntimeError,
    )

    def failing_loader():
        raise CandidateV2RuntimeError(
            "Candidate v2 advisory "
            "artifact is not installed."
        )

    monkeypatch.setattr(
        "leakguard.cli."
        "load_frozen_candidate_v2_runtime",
        failing_loader,
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--ml-advisory",
        ],
    )

    assert result.exit_code == 2

    assert (
        "Unable to enable"
        in result.stdout
    )

    assert (
        "not installed"
        in result.stdout
    )


def test_ml_advisory_does_not_change_known_pattern_authority(
    tmp_path,
    monkeypatch,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    test_file = (
        tmp_path
        / "config.py"
    )

    test_file.write_text(
        f'DB_PASSWORD = "{secret}"',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "leakguard.cli."
        "load_frozen_candidate_v2_runtime",
        lambda: StubRuntime(),
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--ml-advisory",
        ],
    )

    assert result.exit_code == 1

    assert "Hardcoded" in (
        result.stdout
    )

    assert "Password" in (
        result.stdout
    )

    assert "HIGH" in (
        result.stdout
    )

    assert secret not in (
        result.stdout
    )
