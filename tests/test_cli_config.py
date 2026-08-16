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


def write_ml_config(
    root,
    enabled,
    mode="advisory",
):
    config_file = (
        root
        / ".leakguard.toml"
    )

    enabled_text = (
        "true"
        if enabled
        else "false"
    )

    config_file.write_text(
        (
            "[ml]\n"
            f"enabled = {enabled_text}\n"
            f'mode = "{mode}"\n'
        ),
        encoding="utf-8",
    )


def test_project_config_can_enable_ml_advisory(
    tmp_path,
    monkeypatch,
):
    write_ml_config(
        tmp_path,
        enabled=True,
    )

    secret = (
        "K7mP2xQ9vL4sN8zA1c"
    )

    test_file = (
        tmp_path
        / "mystery.py"
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
        ],
    )

    assert result.exit_code == 1

    assert len(
        calls
    ) == 1

    assert (
        "ML Advisory: Candidate v2"
        in result.stdout
    )

    assert (
        "87.3%"
        in result.stdout
    )

    assert secret not in (
        result.stdout
    )


def test_no_ml_advisory_overrides_enabled_config(
    tmp_path,
    monkeypatch,
):
    write_ml_config(
        tmp_path,
        enabled=True,
    )

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
            "when --no-ml-advisory "
            "is supplied."
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
            "--no-ml-advisory",
        ],
    )

    assert result.exit_code == 0

    assert (
        "Security scan passed"
        in result.stdout
    )

    assert (
        "ML Advisory: Candidate v2"
        not in result.stdout
    )


def test_ml_advisory_overrides_disabled_config(
    tmp_path,
    monkeypatch,
):
    write_ml_config(
        tmp_path,
        enabled=False,
    )

    secret = (
        "K7mP2xQ9vL4sN8zA1c"
    )

    test_file = (
        tmp_path
        / "mystery.py"
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
        "ML Advisory: Candidate v2"
        in result.stdout
    )


def test_blocking_config_is_rejected_by_cli(
    tmp_path,
):
    write_ml_config(
        tmp_path,
        enabled=True,
        mode="blocking",
    )

    test_file = (
        tmp_path
        / "app.py"
    )

    test_file.write_text(
        'message = "Hello world"',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 2

    assert (
        "Invalid LeakGuard configuration"
        in result.stdout
    )

    assert (
        "only 'advisory'"
        in result.stdout
    )


def test_conflicting_ml_flags_are_rejected(
    tmp_path,
):
    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
            "--ml-advisory",
            "--no-ml-advisory",
        ],
    )

    assert result.exit_code == 2

    assert (
        "Conflicting ML options"
        in result.stdout
    )

    assert (
        "cannot be used together"
        in result.stdout
    )
