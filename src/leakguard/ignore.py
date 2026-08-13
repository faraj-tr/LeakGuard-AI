from fnmatch import fnmatch
from pathlib import Path


IGNORE_FILE_NAME = ".leakguardignore"


def load_ignore_patterns(root: Path) -> list[str]:
    """
    Load LeakGuard ignore rules from the scan root.

    Blank lines and comments beginning with #
    are ignored.
    """

    ignore_file = root / IGNORE_FILE_NAME

    if not ignore_file.is_file():
        return []

    try:
        content = ignore_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except OSError:
        return []

    patterns = []

    for line in content.splitlines():
        pattern = line.strip()

        if not pattern:
            continue

        if pattern.startswith("#"):
            continue

        patterns.append(
            pattern.replace("\\", "/")
        )

    return patterns


def is_ignored(
    path: Path,
    root: Path,
    patterns: list[str],
) -> bool:
    """
    Check whether a path matches any LeakGuard
    ignore rule.

    Supported examples:

        demo_project/
        tests/fixtures/
        *.log
        generated.json
    """

    try:
        relative_path = (
            path.resolve()
            .relative_to(root.resolve())
            .as_posix()
        )

    except ValueError:
        return False

    for pattern in patterns:
        normalized_pattern = (
            pattern.strip()
            .replace("\\", "/")
        )

        if not normalized_pattern:
            continue

        if normalized_pattern.startswith("/"):
            normalized_pattern = (
                normalized_pattern[1:]
            )

        # Directory rule:
        # demo_project/
        if normalized_pattern.endswith("/"):
            directory = normalized_pattern.rstrip("/")

            if (
                relative_path == directory
                or relative_path.startswith(
                    f"{directory}/"
                )
            ):
                return True

            continue

        # Full relative path / glob rule.
        if fnmatch(
            relative_path,
            normalized_pattern,
        ):
            return True

        # File-name glob rule:
        # *.log
        if fnmatch(
            path.name,
            normalized_pattern,
        ):
            return True

    return False