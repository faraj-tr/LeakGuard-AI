from pathlib import Path

from leakguard.candidate import analyze_candidate
from leakguard.extractor import extract_assignment
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
    Scan one file for known and unknown
    possible secret exposures.
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

        known_pattern_found = False

        # Layer 1:
        # Search for known secret patterns.
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
                        "candidate_score": None,
                        "reasons": [],
                    }
                )

                known_pattern_found = True

        # Avoid duplicate findings when a stronger
        # known detector already matched the line.
        if known_pattern_found:
            continue

        # Layer 2:
        # Extract generic assignments such as:
        # x = "something"
        assignment = extract_assignment(line)

        if assignment is None:
            continue

        variable_name = assignment["variable_name"]
        raw_value = assignment["value"]

        # Layer 3:
        # Analyze unknown values using heuristic signals.
        analysis = analyze_candidate(
            variable_name=variable_name,
            value=raw_value,
        )

        if not analysis["is_suspicious"]:
            continue

        findings.append(
            {
                "file": str(path),
                "line": line_number,
                "type": "Unknown Secret Candidate",
                "severity": "MEDIUM",
                "masked_value": mask_secret(raw_value),
                "candidate_score": analysis["score"],
                "reasons": analysis["reasons"],
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