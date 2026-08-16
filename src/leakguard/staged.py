import subprocess
from pathlib import Path
from typing import Any

from leakguard.ignore import (
    load_ignore_patterns,
)
from leakguard.scan_safety import (
    build_scan_limitation_finding,
    evaluate_content_bytes,
    evaluate_file_size,
)
from leakguard.scanner import (
    is_supported_file,
    scan_content,
    should_skip,
)


REGULAR_GIT_FILE_MODES = {
    "100644",
    "100755",
}


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

    for raw_path in output.split(
        b"\0"
    ):

        if not raw_path:
            continue

        relative_path = raw_path.decode(
            "utf-8",
            errors="surrogateescape",
        )

        staged_files.append(
            Path(
                relative_path
            )
        )

    return staged_files


def get_staged_index_modes(
    root: Path,
) -> dict[str, str]:
    """
    Return Git index modes keyed by their
    project-relative POSIX paths.

    Git mode allows LeakGuard to distinguish
    regular staged blobs from symbolic links
    and other non-regular index entries.
    """

    output = run_git_command(
        root,
        [
            "ls-files",
            "--stage",
            "-z",
        ],
    )

    modes = {}

    for record in output.split(
        b"\0"
    ):

        if not record:
            continue

        try:
            metadata, raw_path = (
                record.split(
                    b"\t",
                    maxsplit=1,
                )
            )

        except ValueError as error:
            raise GitStagedScanError(
                "Git returned malformed "
                "index metadata."
            ) from error

        fields = metadata.split()

        if len(
            fields
        ) != 3:
            raise GitStagedScanError(
                "Git returned malformed "
                "index metadata."
            )

        raw_mode, _, raw_stage = (
            fields
        )

        if raw_stage != b"0":
            raise GitStagedScanError(
                "Unmerged Git index entries "
                "cannot be scanned safely."
            )

        try:
            mode = raw_mode.decode(
                "ascii"
            )

        except UnicodeDecodeError as error:
            raise GitStagedScanError(
                "Git returned an invalid "
                "index file mode."
            ) from error

        relative_path = raw_path.decode(
            "utf-8",
            errors="surrogateescape",
        )

        modes[
            Path(
                relative_path
            ).as_posix()
        ] = mode

    return modes


def get_staged_file_size(
    root: Path,
    relative_path: Path,
) -> int:
    """
    Ask Git for the staged blob size without
    loading the blob content.

    This occurs before git show so oversized
    staged files cannot force LeakGuard to
    buffer their complete contents first.
    """

    git_path = (
        relative_path
        .as_posix()
    )

    output = run_git_command(
        root,
        [
            "cat-file",
            "-s",
            f":{git_path}",
        ],
    )

    try:
        return int(
            output.decode(
                "ascii"
            ).strip()
        )

    except (
        UnicodeDecodeError,
        ValueError,
    ) as error:
        raise GitStagedScanError(
            "Git returned an invalid "
            "staged blob size."
        ) from error


def read_staged_file_bytes(
    root: Path,
    relative_path: Path,
) -> bytes:
    """
    Read the exact staged blob as bytes.

    Callers must validate index mode and
    staged size before invoking this function.
    """

    git_path = (
        relative_path
        .as_posix()
    )

    return run_git_command(
        root,
        [
            "show",
            f":{git_path}",
        ],
    )


def read_staged_file(
    root: Path,
    relative_path: Path,
) -> str:
    """
    Backward-compatible text reader for
    staged file content.
    """

    content = (
        read_staged_file_bytes(
            root=root,
            relative_path=(
                relative_path
            ),
        )
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

    Supported staged blobs are validated for:
    - project path scope
    - ignore rules
    - Git index file mode
    - size
    - binary content

    Non-regular supported entries fail closed.
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

    staged_modes = (
        get_staged_index_modes(
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
            ignore_patterns=(
                ignore_patterns
            ),
        ):
            continue

        if not is_supported_file(
            absolute_path
        ):
            continue

        git_path = (
            relative_path
            .as_posix()
        )

        git_mode = (
            staged_modes.get(
                git_path
            )
        )

        if git_mode is None:
            raise GitStagedScanError(
                "Unable to determine the "
                "staged Git file mode for "
                f"{git_path}."
            )

        files_scanned += 1

        if (
            git_mode
            not in REGULAR_GIT_FILE_MODES
        ):

            findings.append(
                build_scan_limitation_finding(
                    path=absolute_path,
                    reason=(
                        "Staged Git entry is "
                        "not a regular file "
                        f"(mode {git_mode})."
                    ),
                )
            )

            continue

        staged_size = (
            get_staged_file_size(
                root=root,
                relative_path=(
                    relative_path
                ),
            )
        )

        size_result = (
            evaluate_file_size(
                staged_size
            )
        )

        if not size_result.safe_to_scan:

            findings.append(
                build_scan_limitation_finding(
                    path=absolute_path,
                    reason=(
                        size_result.reason
                        or "Staged file could "
                        "not be scanned safely."
                    ),
                )
            )

            continue

        raw_content = (
            read_staged_file_bytes(
                root=root,
                relative_path=(
                    relative_path
                ),
            )
        )

        content_result = (
            evaluate_content_bytes(
                raw_content
            )
        )

        if not (
            content_result.safe_to_scan
        ):

            findings.append(
                build_scan_limitation_finding(
                    path=absolute_path,
                    reason=(
                        content_result.reason
                        or "Staged file could "
                        "not be scanned safely."
                    ),
                )
            )

            continue

        content = raw_content.decode(
            "utf-8",
            errors="ignore",
        )

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
