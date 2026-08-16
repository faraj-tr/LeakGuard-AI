import os
from fnmatch import fnmatch
from pathlib import Path


IGNORE_FILE_NAME = ".leakguardignore"


def get_project_relative_path(
    path: Path,
    root: Path,
) -> Path | None:
    """
    Return a lexically normalized path relative
    to the scan root.

    os.path.abspath is used deliberately
    instead of Path.resolve().

    This normalizes "." and ".." without
    following symbolic links, so ignore rules
    are applied to the path that actually
    appears inside the project.
    """

    root_path = (
        Path(
            os.path.abspath(
                os.fspath(
                    Path(root)
                    .expanduser()
                )
            )
        )
    )

    candidate = (
        Path(path)
        .expanduser()
    )

    if not candidate.is_absolute():
        candidate = (
            root_path
            / candidate
        )

    candidate_path = Path(
        os.path.abspath(
            os.fspath(
                candidate
            )
        )
    )

    try:
        return (
            candidate_path
            .relative_to(
                root_path
            )
        )

    except ValueError:
        return None


def normalize_ignore_pattern(
    pattern: str,
) -> str:
    """
    Normalize path separators while
    preserving LeakGuard ignore semantics.
    """

    normalized = (
        pattern.strip()
        .replace(
            "\\",
            "/",
        )
    )

    while normalized.startswith(
        "./"
    ):
        normalized = normalized[
            2:
        ]

    return normalized


def load_ignore_patterns(
    root: Path,
) -> list[str]:
    """
    Load LeakGuard ignore rules from the
    scan root.

    Blank lines and comments beginning with #
    are ignored.

    UTF-8 BOM is tolerated because Windows
    PowerShell and some editors may emit it.
    """

    ignore_file = (
        Path(root)
        / IGNORE_FILE_NAME
    )

    if not ignore_file.is_file():
        return []

    try:
        raw_content = (
            ignore_file
            .read_bytes()
        )

    except OSError:
        # Failure to load ignore rules makes
        # LeakGuard scan more, not less.
        return []

    content = raw_content.decode(
        "utf-8-sig",
        errors="ignore",
    )

    patterns = []

    for line in content.splitlines():

        pattern = (
            normalize_ignore_pattern(
                line
            )
        )

        if not pattern:
            continue

        if pattern.startswith(
            "#"
        ):
            continue

        patterns.append(
            pattern
        )

    return patterns


def is_ignored(
    path: Path,
    root: Path,
    patterns: list[str],
) -> bool:
    """
    Check whether a project-relative lexical
    path matches any LeakGuard ignore rule.

    Symbolic links are not resolved while
    applying ignore rules.
    """

    relative = (
        get_project_relative_path(
            path=path,
            root=root,
        )
    )

    if relative is None:
        return False

    relative_path = (
        relative
        .as_posix()
    )

    for pattern in patterns:

        normalized_pattern = (
            normalize_ignore_pattern(
                pattern
            )
        )

        if not normalized_pattern:
            continue

        if normalized_pattern.startswith(
            "/"
        ):
            normalized_pattern = (
                normalized_pattern[
                    1:
                ]
            )

        # Directory rule:
        # demo_project/
        if normalized_pattern.endswith(
            "/"
        ):

            directory = (
                normalized_pattern
                .rstrip(
                    "/"
                )
            )

            if (
                relative_path
                == directory
                or relative_path.startswith(
                    f"{directory}/"
                )
            ):
                return True

            continue

        # Full project-relative path / glob.
        if fnmatch(
            relative_path,
            normalized_pattern,
        ):
            return True

        # Basename rule:
        # *.log
        # generated.json
        if fnmatch(
            relative.name,
            normalized_pattern,
        ):
            return True

    return False
