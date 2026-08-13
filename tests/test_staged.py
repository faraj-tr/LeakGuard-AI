import subprocess

import pytest

from leakguard.staged import (
    GitStagedScanError,
    scan_staged_path,
)


def initialize_git_repository(
    root,
):
    subprocess.run(
        [
            "git",
            "init",
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def stage_file(
    root,
    file_name,
):
    subprocess.run(
        [
            "git",
            "add",
            file_name,
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_staged_scan_detects_staged_secret(
    tmp_path,
):
    initialize_git_repository(
        tmp_path
    )

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_STAGE_123"
    )

    config_file = (
        tmp_path
        / "config.py"
    )

    config_file.write_text(
        f'DB_PASSWORD = "{secret}"',
        encoding="utf-8",
    )

    stage_file(
        tmp_path,
        "config.py",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert (
        findings[0]["type"]
        == "Hardcoded Password"
    )

    assert secret not in str(
        findings
    )


def test_staged_scan_uses_staged_version_not_working_tree(
    tmp_path,
):
    initialize_git_repository(
        tmp_path
    )

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_STAGE_123"
    )

    config_file = (
        tmp_path
        / "config.py"
    )

    # Dangerous version enters staging.
    config_file.write_text(
        f'DB_PASSWORD = "{secret}"',
        encoding="utf-8",
    )

    stage_file(
        tmp_path,
        "config.py",
    )

    # Working-tree version is made safe
    # after staging.
    config_file.write_text(
        'message = "Hello world"',
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert (
        findings[0]["type"]
        == "Hardcoded Password"
    )


def test_staged_scan_ignores_unstaged_secret(
    tmp_path,
):
    initialize_git_repository(
        tmp_path
    )

    app_file = (
        tmp_path
        / "app.py"
    )

    # Safe version is staged.
    app_file.write_text(
        'message = "Hello world"',
        encoding="utf-8",
    )

    stage_file(
        tmp_path,
        "app.py",
    )

    # Dangerous version exists only
    # in the working tree.
    app_file.write_text(
        (
            'DB_PASSWORD = '
            '"LEAKGUARD_FAKE_PASSWORD_UNSTAGED_123"'
        ),
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert findings == []


def test_staged_scan_respects_leakguardignore(
    tmp_path,
):
    initialize_git_repository(
        tmp_path
    )

    ignored_directory = (
        tmp_path
        / "fixtures"
    )

    ignored_directory.mkdir()

    secret_file = (
        ignored_directory
        / "config.py"
    )

    secret_file.write_text(
        (
            'DB_PASSWORD = '
            '"LEAKGUARD_FAKE_PASSWORD_IGNORE_123"'
        ),
        encoding="utf-8",
    )

    ignore_file = (
        tmp_path
        / ".leakguardignore"
    )

    ignore_file.write_text(
        "fixtures/\n",
        encoding="utf-8",
    )

    stage_file(
        tmp_path,
        "fixtures/config.py",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 0
    assert findings == []


def test_staged_scan_requires_git_repository(
    tmp_path,
):
    with pytest.raises(
        GitStagedScanError
    ):
        scan_staged_path(
            tmp_path
        )