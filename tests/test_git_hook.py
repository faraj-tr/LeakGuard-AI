import pytest

from leakguard.git_hook import (
    ExistingHookError,
    HOOK_MARKER,
    NotGitRepositoryError,
    PRE_COMMIT_HOOK,
    install_pre_commit_hook,
)


def test_installs_pre_commit_hook(
    tmp_path,
):
    hooks_directory = (
        tmp_path
        / ".git"
        / "hooks"
    )

    hooks_directory.mkdir(
        parents=True
    )

    hook_path = (
        install_pre_commit_hook(
            tmp_path
        )
    )

    assert hook_path.exists()

    content = hook_path.read_text(
        encoding="utf-8"
    )

    assert HOOK_MARKER in content

    assert (
        "scan . --staged"
        in content
    )

    assert "exit 0" in content


def test_installer_refuses_to_overwrite_custom_hook(
    tmp_path,
):
    hooks_directory = (
        tmp_path
        / ".git"
        / "hooks"
    )

    hooks_directory.mkdir(
        parents=True
    )

    hook_path = (
        hooks_directory
        / "pre-commit"
    )

    hook_path.write_text(
        "#!/bin/sh\n"
        "echo custom-hook\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ExistingHookError
    ):
        install_pre_commit_hook(
            tmp_path
        )


def test_installer_updates_existing_leakguard_hook(
    tmp_path,
):
    hooks_directory = (
        tmp_path
        / ".git"
        / "hooks"
    )

    hooks_directory.mkdir(
        parents=True
    )

    hook_path = (
        hooks_directory
        / "pre-commit"
    )

    hook_path.write_text(
        f"{HOOK_MARKER}\n"
        "old LeakGuard hook",
        encoding="utf-8",
    )

    installed_path = (
        install_pre_commit_hook(
            tmp_path
        )
    )

    content = (
        installed_path.read_text(
            encoding="utf-8"
        )
    )

    assert content == PRE_COMMIT_HOOK


def test_installer_requires_git_repository(
    tmp_path,
):
    with pytest.raises(
        NotGitRepositoryError
    ):
        install_pre_commit_hook(
            tmp_path
        )