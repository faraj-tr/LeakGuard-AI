from typer.testing import CliRunner

from leakguard.cli import app
from leakguard.scanner import (
    scan_path,
)


runner = CliRunner()


def test_source_scanner_excludes_artifact_owned_files(
    tmp_path,
):
    source_file = (
        tmp_path
        / "src"
        / "app.js"
    )

    artifact_file = (
        tmp_path
        / "dist"
        / "assets"
        / "app.js"
    )

    source_file.parent.mkdir(
        parents=True,
    )

    artifact_file.parent.mkdir(
        parents=True,
    )

    source_file.write_text(
        'console.log("safe source");',
        encoding="utf-8",
    )

    artifact_file.write_text(
        (
            'const password='
            '"LEAKGUARD_FAKE_PASSWORD_123";'
        ),
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert findings == []


def test_cli_normal_scan_detects_artifact_propagation_once(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    env_file = (
        tmp_path
        / ".env"
    )

    env_file.write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact_file = (
        tmp_path
        / "dist"
        / "assets"
        / "app.js"
    )

    artifact_file.parent.mkdir(
        parents=True,
    )

    artifact_file.write_text(
        (
            'const config={key:"'
            f'{secret}'
            '"};'
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "scan",
            str(
                tmp_path
            ),
            "--no-ml-advisory",
        ],
    )

    # The source .env finding and the
    # artifact exposure both block.
    assert result.exit_code == 1

    # .env is owned by the source scanner.
    # dist/assets/app.js is owned by the
    # artifact scanner. Neither is counted
    # twice.
    assert "Files scanned: 2" in (
        result.stdout
    )

    # Rich may wrap the multi-word finding
    # label across terminal lines. The exact
    # finding type itself is already verified
    # by the artifact-engine unit tests, so
    # this CLI integration test verifies the
    # rendered artifact evidence instead of
    # depending on terminal width.
    assert "Artifact" in (
        result.stdout
    )

    assert "Exposure" in (
        result.stdout
    )

    assert "Critical: 1" in (
        result.stdout
    )

    assert "Source variable: API_KEY" in (
        result.stdout
    )

    assert secret not in (
        result.stdout
    )


def test_build_and_next_static_are_not_double_scanned(
    tmp_path,
):
    source_file = (
        tmp_path
        / "app.js"
    )

    build_file = (
        tmp_path
        / "build"
        / "app.js"
    )

    next_file = (
        tmp_path
        / ".next"
        / "static"
        / "chunk.js"
    )

    source_file.write_text(
        'console.log("source");',
        encoding="utf-8",
    )

    build_file.parent.mkdir(
        parents=True,
    )

    next_file.parent.mkdir(
        parents=True,
    )

    build_file.write_text(
        'console.log("build");',
        encoding="utf-8",
    )

    next_file.write_text(
        'console.log("next");',
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert findings == []
