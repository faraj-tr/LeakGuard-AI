import stat
from pathlib import Path


HOOK_FILE_NAME = "pre-commit"

HOOK_MARKER = (
    "# LeakGuard AI managed pre-commit hook"
)


PRE_COMMIT_HOOK = """#!/bin/sh
# LeakGuard AI managed pre-commit hook

echo ""
echo "LeakGuard AI: running pre-commit security gate..."
echo ""

if [ -x ".venv/Scripts/python.exe" ]; then
    ".venv/Scripts/python.exe" -m leakguard.cli scan .
    status=$?

elif [ -x ".venv/bin/python" ]; then
    ".venv/bin/python" -m leakguard.cli scan .
    status=$?

elif command -v leakguard >/dev/null 2>&1; then
    leakguard scan .
    status=$?

else
    python -m leakguard.cli scan .
    status=$?
fi

if [ "$status" -ne 0 ]; then
    echo ""
    echo "LeakGuard AI blocked this commit."
    echo "Resolve the security findings before committing."
    exit "$status"
fi

echo ""
echo "LeakGuard AI security gate passed."
exit 0
"""


class NotGitRepositoryError(Exception):
    """
    Raised when LeakGuard cannot find
    a .git directory.
    """

    pass


class ExistingHookError(Exception):
    """
    Raised when a user already has a
    pre-commit hook that LeakGuard does
    not own.
    """

    pass


def get_git_hooks_directory(
    project_root: Path,
) -> Path:
    """
    Return the .git/hooks directory
    for a Git repository.
    """

    project_root = project_root.resolve()

    git_directory = (
        project_root
        / ".git"
    )

    if not git_directory.is_dir():
        raise NotGitRepositoryError(
            "No .git directory was found."
        )

    hooks_directory = (
        git_directory
        / "hooks"
    )

    hooks_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return hooks_directory


def install_pre_commit_hook(
    project_root: Path,
) -> Path:
    """
    Install LeakGuard's Git pre-commit hook.

    Existing hooks that were not created
    by LeakGuard are never overwritten.
    """

    hooks_directory = (
        get_git_hooks_directory(
            project_root
        )
    )

    hook_path = (
        hooks_directory
        / HOOK_FILE_NAME
    )

    if hook_path.exists():

        existing_content = (
            hook_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )

        if (
            HOOK_MARKER
            not in existing_content
        ):
            raise ExistingHookError(
                "An existing pre-commit hook "
                "was found. LeakGuard will not "
                "overwrite a hook it does not own."
            )

    hook_path.write_text(
        PRE_COMMIT_HOOK,
        encoding="utf-8",
        newline="\n",
    )

    try:
        current_mode = (
            hook_path.stat().st_mode
        )

        hook_path.chmod(
            current_mode
            | stat.S_IEXEC
        )

    except OSError:
        # Windows may not require Unix-style
        # executable permissions.
        pass

    return hook_path