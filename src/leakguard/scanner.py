from pathlib import Path

from leakguard.masking import mask_secret
from leakguard.patterns import SECRET_PATTERNS


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".html",
}


SPECIAL_FILES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
}


SKIP_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}


def is_supported_file(path: Path) -> bool:
    """
    Check whether LeakGuard should scan this file.
    """

    return (
        path.suffix.lower() in SUPPORTED_EXTENSIONS
        or path.name in SPECIAL_FILES
    )


def should_skip(path: Path) -> bool:
    """
    Ignore directories that should not be scanned.
    """

    return any(
        part in SKIP_DIRECTORIES
        for part in path.parts
    )


def scan_file(path: Path) -> list[dict]:
    """
    Scan one file for possible secrets.
    """

    findings = []

    try:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except OSError:
        return findings

    for line_number, line in enumerate(
        content.splitlines(),
        start=1,
    ):

        for detector in SECRET_PATTERNS:

            for match in detector["pattern"].finditer(line):

                raw_secret = match.group("secret")

                findings.append(
                    {
                        "file": str(path),
                        "line": line_number,
                        "type": detector["name"],
                        "severity": detector["severity"],
                        "masked_value": mask_secret(raw_secret),
                    }
                )

    return findings


def scan_path(root: Path) -> tuple[int, list[dict]]:
    """
    Scan all supported files inside a project directory.
    """

    root = root.resolve()

    files_scanned = 0
    findings = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if should_skip(path):
            continue

        if not is_supported_file(path):
            continue

        files_scanned += 1

        findings.extend(
            scan_file(path)
        )

    return files_scanned, findings