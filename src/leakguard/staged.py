import subprocess
from pathlib import Path
from typing import Any

from leakguard.ignore import (
    load_ignore_patterns,
)
from leakguard.scanner import (
    is_supported_file,
    scan_content,
    should_skip,
)


class GitStagedScanError(Exception):
    """
    Raised when LeakGuard cannot inspect
    the Git staging area.
    """

    pass


def run_git_command(
    root: Path,
    arguments: list[str],
) -> bytes:
    """
    Run a Git command inside the repository.
    """

    try:
        result = subprocess.run(
            [
                "git",
                *arguments,
            ],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    except OSError as error:
        raise GitStagedScanError(
            "Git could not be executed."
        ) from error

    if result.returncode != 0:

        error_message = (
            result.stderr.decode(
                "utf-8",
                errors="ignore",
            ).strip()
        )

        raise GitStagedScanError(
            error_message
            or "Git command failed."
        )

    return result.stdout


def get_staged_files(
    root: Path,
) -> list[Path]:
    """
    Return files currently staged for commit.

    Added, copied, modified and renamed files
    are included.

    Deleted files are ignored because there is
    no staged content left to scan.
    """

    output = run_git_command(
        root,
        [
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMR",
            "-z",
        ],
    )

    staged_files = []

    for raw_path in output.split(b"\0"):

        if not raw_path:
            continue

        relative_path = raw_path.decode(
            "utf-8",
            errors="surrogateescape",
        )

        staged_files.append(
            Path(relative_path)
        )

    return staged_files


def read_staged_file(
    root: Path,
    relative_path: Path,
) -> str:
    """
    Read the exact version of a file stored
    in Git's staging area.
    """

    git_path = (
        relative_path
        .as_posix()
    )

    content = run_git_command(
        root,
        [
            "show",
            f":{git_path}",
        ],
    )

    return content.decode(
        "utf-8",
        errors="ignore",
    )


def scan_staged_path(
    root: Path,
    ml_advisory_runtime: Any | None = None,
) -> tuple[int, list[dict]]:
    """
    Scan only content currently staged
    for the next Git commit.

    A supplied ML advisory runtime is reused
    across every staged file.
    """

    root = root.resolve()

    git_directory = (
        root
        / ".git"
    )

    if not git_directory.exists():

        raise GitStagedScanError(
            "No Git repository was found."
        )

    ignore_patterns = (
        load_ignore_patterns(
            root
        )
    )

    staged_files = (
        get_staged_files(
            root
        )
    )

    files_scanned = 0
    findings = []

    for relative_path in staged_files:

        absolute_path = (
            root
            / relative_path
        )

        if should_skip(
            path=absolute_path,
            root=root,
            ignore_patterns=ignore_patterns,
        ):
            continue

        if not is_supported_file(
            absolute_path
        ):
            continue

        content = read_staged_file(
            root=root,
            relative_path=relative_path,
        )

        files_scanned += 1

        findings.extend(
            scan_content(
                path=absolute_path,
                content=content,
                ml_advisory_runtime=(
                    ml_advisory_runtime
                ),
            )
        )

    return (
        files_scanned,
        findings,
    )
