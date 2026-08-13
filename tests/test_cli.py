from typer.testing import CliRunner

from leakguard.cli import app


runner = CliRunner()


def test_scan_command_passes_clean_project(tmp_path):
    test_file = tmp_path / "app.py"

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

    assert result.exit_code == 0
    assert "Security scan passed" in result.stdout


def test_scan_command_fails_when_secret_is_found(
    tmp_path,
):
    secret = "LEAKGUARD_FAKE_PASSWORD_123"

    test_file = tmp_path / "config.py"

    test_file.write_text(
        f'DB_PASSWORD = "{secret}"',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1

    # Rich may wrap the finding across multiple table lines.
    assert "Hardcoded" in result.stdout
    assert "Password" in result.stdout
    assert "HIGH" in result.stdout

    assert "Security gate failed" in result.stdout

    # Never expose the complete raw secret.
    assert secret not in result.stdout


def test_cli_reports_vite_client_exposure(
    tmp_path,
):
    secret = "LEAKGUARD_FAKE_KEY_ABC123"

    env_file = tmp_path / ".env"

    env_file.write_text(
        f"VITE_OPENAI_API_KEY={secret}",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1

    # Rich may wrap this finding across several rows.
    assert "Client-Side" in result.stdout
    assert "Secret" in result.stdout
    assert "Exposure" in result.stdout

    assert "CRITICAL" in result.stdout
    assert "Vite" in result.stdout

    assert "Security gate failed" in result.stdout

    # Never expose the complete raw secret.
    assert secret not in result.stdout