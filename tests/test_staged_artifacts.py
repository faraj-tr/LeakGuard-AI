import subprocess

from leakguard.artifacts import (
    scan_artifacts,
)
from leakguard.staged import (
    scan_staged_path,
)


def git_init(root):
    subprocess.run(
        ["git", "init"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_add(root, *paths):
    subprocess.run(
        [
            "git",
            "add",
            *paths,
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_staged_artifact_uses_only_staged_dotenv(
    tmp_path,
):
    git_init(tmp_path)

    staged_secret = (
        "LEAKGUARD_FAKE_STAGE_KEY_ABC123"
    )

    working_secret = (
        "LEAKGUARD_FAKE_WORKTREE_KEY_XYZ999"
    )

    env_file = tmp_path / ".env"

    artifact = (
        tmp_path
        / "dist"
        / "app.js.map"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    env_file.write_text(
        f"API_KEY={staged_secret}",
        encoding="utf-8",
    )

    artifact.write_text(
        staged_secret,
        encoding="utf-8",
    )

    git_add(
        tmp_path,
        ".env",
        "dist/app.js.map",
    )

    # Change both working-tree versions after
    # staging. The staged scan must still use
    # the original staged pair.
    env_file.write_text(
        f"API_KEY={working_secret}",
        encoding="utf-8",
    )

    artifact.write_text(
        working_secret,
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 2

    finding_types = {
        finding["type"]
        for finding in findings
    }

    assert "Artifact Secret Exposure" in (
        finding_types
    )

    assert staged_secret not in str(
        findings
    )

    assert working_secret not in str(
        findings
    )


def test_staged_artifact_never_uses_unstaged_dotenv(
    tmp_path,
):
    git_init(tmp_path)

    secret = (
        "LEAKGUARD_FAKE_UNSTAGED_KEY_ABC123"
    )

    env_file = tmp_path / ".env"

    artifact = (
        tmp_path
        / "dist"
        / "app.js.map"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    env_file.write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact.write_text(
        secret,
        encoding="utf-8",
    )

    # Only artifact enters index.
    git_add(
        tmp_path,
        "dist/app.js.map",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert findings == []


def test_unstaged_artifact_is_not_scanned(
    tmp_path,
):
    git_init(tmp_path)

    secret = (
        "LEAKGUARD_FAKE_STAGE_KEY_ABC123"
    )

    env_file = tmp_path / ".env"

    artifact = (
        tmp_path
        / "dist"
        / "app.js"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    env_file.write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact.write_text(
        secret,
        encoding="utf-8",
    )

    # Only env enters index.
    git_add(
        tmp_path,
        ".env",
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 1

    assert not any(
        finding["type"]
        == "Artifact Secret Exposure"
        for finding in findings
    )


def test_normal_artifact_scan_respects_ignore(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    (tmp_path / ".env").write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact = (
        tmp_path
        / "dist"
        / "app.js"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    artifact.write_text(
        secret,
        encoding="utf-8",
    )

    (
        tmp_path
        / ".leakguardignore"
    ).write_text(
        "dist/\n",
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_artifacts(
            tmp_path
        )
    )

    assert files_scanned == 0

    assert not any(
        finding["type"]
        == "Artifact Secret Exposure"
        for finding in findings
    )


def test_ignored_dotenv_does_not_seed_inventory(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    env_directory = (
        tmp_path
        / "config"
    )

    env_directory.mkdir()

    (
        env_directory
        / ".env"
    ).write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact = (
        tmp_path
        / "dist"
        / "app.js"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    artifact.write_text(
        secret,
        encoding="utf-8",
    )

    (
        tmp_path
        / ".leakguardignore"
    ).write_text(
        "config/\n",
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_artifacts(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert findings == []
