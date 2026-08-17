import subprocess
from pathlib import Path
from typing import Any

from leakguard.artifacts import (
    DOTENV_SOURCE_FILES,
    build_dotenv_secret_inventory_from_content,
    is_artifact_path,
    is_supported_artifact_file,
    scan_artifact_content,
)
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

        staged_files.append(
            Path(
                raw_path.decode(
                    "utf-8",
                    errors="surrogateescape",
                )
            )
        )

    return staged_files


def get_staged_index_modes(
    root: Path,
) -> dict[str, str]:
    """
    Return Git index modes keyed by
    project-relative POSIX path.
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

        if len(fields) != 3:
            raise GitStagedScanError(
                "Git returned malformed "
                "index metadata."
            )

        raw_mode, _, raw_stage = fields

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
    Read staged blob size before loading it.
    """

    git_path = (
        relative_path.as_posix()
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
    """

    return run_git_command(
        root,
        [
            "show",
            f":{relative_path.as_posix()}",
        ],
    )


def read_staged_file(
    root: Path,
    relative_path: Path,
) -> str:
    """
    Backward-compatible staged text reader.
    """

    return read_staged_file_bytes(
        root=root,
        relative_path=relative_path,
    ).decode(
        "utf-8",
        errors="ignore",
    )


def scan_staged_path(
    root: Path,
    ml_advisory_runtime: Any | None = None,
) -> tuple[int, list[dict]]:
    """
    Scan the exact content staged for the next
    Git commit.

    Source findings use staged source blobs.

    Artifact propagation uses only:
    staged dotenv values
        versus
    staged artifact content.

    Working-tree dotenv values are never used
    to classify staged artifacts.
    """

    root = root.resolve()

    if not (
        root
        / ".git"
    ).exists():
        raise GitStagedScanError(
            "No Git repository was found."
        )

    ignore_patterns = (
        load_ignore_patterns(
            root
        )
    )

    staged_files = sorted(
        get_staged_files(
            root
        ),
        key=lambda candidate: (
            candidate.as_posix()
        ),
    )

    staged_modes = (
        get_staged_index_modes(
            root
        )
    )

    files_scanned = 0

    # Records preserve deterministic staged
    # ordering while allowing inventory to be
    # built before artifact comparison.
    records = []

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

        artifact_owned = (
            is_artifact_path(
                path=absolute_path,
                root=root,
            )
        )

        if artifact_owned:
            supported = (
                is_supported_artifact_file(
                    absolute_path
                )
            )
        else:
            supported = (
                is_supported_file(
                    absolute_path
                )
            )

        if not supported:
            continue

        git_path = (
            relative_path.as_posix()
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
            records.append(
                (
                    "limitation",
                    absolute_path,
                    build_scan_limitation_finding(
                        path=absolute_path,
                        reason=(
                            "Staged Git entry is "
                            "not a regular file "
                            f"(mode {git_mode})."
                        ),
                    ),
                )
            )

            continue

        staged_size = (
            get_staged_file_size(
                root=root,
                relative_path=relative_path,
            )
        )

        size_result = (
            evaluate_file_size(
                staged_size
            )
        )

        if not size_result.safe_to_scan:
            records.append(
                (
                    "limitation",
                    absolute_path,
                    build_scan_limitation_finding(
                        path=absolute_path,
                        reason=(
                            size_result.reason
                            or (
                                "Staged file could "
                                "not be scanned safely."
                            )
                        ),
                    ),
                )
            )

            continue

        raw_content = (
            read_staged_file_bytes(
                root=root,
                relative_path=relative_path,
            )
        )

        content_result = (
            evaluate_content_bytes(
                raw_content
            )
        )

        if not content_result.safe_to_scan:
            records.append(
                (
                    "limitation",
                    absolute_path,
                    build_scan_limitation_finding(
                        path=absolute_path,
                        reason=(
                            content_result.reason
                            or (
                                "Staged file could "
                                "not be scanned safely."
                            )
                        ),
                    ),
                )
            )

            continue

        content = raw_content.decode(
            "utf-8-sig",
            errors="ignore",
        )

        record_type = (
            "artifact"
            if artifact_owned
            else "source"
        )

        records.append(
            (
                record_type,
                absolute_path,
                content,
            )
        )

    # ======================================
    # Build inventory only from staged envs
    # ======================================

    inventory = []
    seen_raw_values: set[str] = set()

    for (
        record_type,
        absolute_path,
        payload,
    ) in records:
        if record_type != "source":
            continue

        if (
            absolute_path.name
            not in DOTENV_SOURCE_FILES
        ):
            continue

        assert isinstance(
            payload,
            str,
        )

        inventory.extend(
            build_dotenv_secret_inventory_from_content(
                source_file=absolute_path,
                content=payload,
                seen_raw_values=(
                    seen_raw_values
                ),
            )
        )

    # ======================================
    # Emit deterministic findings
    # ======================================

    findings = []

    for (
        record_type,
        absolute_path,
        payload,
    ) in records:
        if record_type == "limitation":
            assert isinstance(
                payload,
                dict,
            )

            findings.append(
                payload
            )

            continue

        assert isinstance(
            payload,
            str,
        )

        if record_type == "artifact":
            findings.extend(
                scan_artifact_content(
                    path=absolute_path,
                    content=payload,
                    inventory=inventory,
                )
            )

            continue

        findings.extend(
            scan_content(
                path=absolute_path,
                content=payload,
                ml_advisory_runtime=(
                    ml_advisory_runtime
                ),
            )
        )

    return (
        files_scanned,
        findings,
    )
