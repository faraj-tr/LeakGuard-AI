from pathlib import Path

from leakguard.candidate import analyze_candidate
from leakguard.client_exposure import analyze_client_exposure
from leakguard.dotenv import extract_dotenv_assignment
from leakguard.extractor import extract_assignment
from leakguard.ignore import (
    is_ignored,
    load_ignore_patterns,
)
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


def is_dotenv_file(path: Path) -> bool:
    """
    Check whether the file is a supported
    environment configuration file.
    """

    return path.name in SPECIAL_FILES


def should_skip(
    path: Path,
    root: Path,
    ignore_patterns: list[str],
) -> bool:
    """
    Check whether a file should be skipped because
    it belongs to a built-in ignored directory or
    matches .leakguardignore.
    """

    if any(
        part in SKIP_DIRECTORIES
        for part in path.parts
    ):
        return True

    return is_ignored(
        path=path,
        root=root,
        patterns=ignore_patterns,
    )


def scan_file(path: Path) -> list[dict]:
    """
    Scan one file for possible secret exposures.

    Detection priority:

    1. Client-side environment exposure
    2. Known secret patterns
    3. Generic heuristic candidates
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

        # =================================
        # Layer 1:
        # Client-side environment exposure
        # =================================

        if is_dotenv_file(path):
            dotenv_assignment = (
                extract_dotenv_assignment(line)
            )

            if dotenv_assignment is not None:
                variable_name = (
                    dotenv_assignment[
                        "variable_name"
                    ]
                )

                raw_value = (
                    dotenv_assignment[
                        "value"
                    ]
                )

                exposure = analyze_client_exposure(
                    variable_name=variable_name,
                    value=raw_value,
                )

                if exposure["is_risky"]:
                    findings.append(
                        {
                            "file": str(path),
                            "line": line_number,
                            "type": (
                                "Client-Side Secret Exposure"
                            ),
                            "severity": exposure[
                                "severity"
                            ],
                            "masked_value": mask_secret(
                                raw_value
                            ),
                            "candidate_score": exposure[
                                "candidate_score"
                            ],
                            "framework": exposure[
                                "framework"
                            ],
                            "reasons": exposure[
                                "reasons"
                            ],
                        }
                    )

                    # Client exposure is more specific
                    # than the generic detectors.
                    continue

        # =================================
        # Layer 2:
        # Known secret patterns
        # =================================

        known_pattern_found = False

        for detector in SECRET_PATTERNS:
            for match in detector[
                "pattern"
            ].finditer(line):

                raw_secret = match.group(
                    "secret"
                )

                findings.append(
                    {
                        "file": str(path),
                        "line": line_number,
                        "type": detector[
                            "name"
                        ],
                        "severity": detector[
                            "severity"
                        ],
                        "masked_value": mask_secret(
                            raw_secret
                        ),
                        "candidate_score": None,
                        "framework": None,
                        "reasons": [],
                    }
                )

                known_pattern_found = True

        if known_pattern_found:
            continue

        # =================================
        # Layer 3:
        # Generic assignment extraction
        # =================================

        assignment = extract_assignment(
            line
        )

        if assignment is None:
            continue

        variable_name = assignment[
            "variable_name"
        ]

        raw_value = assignment[
            "value"
        ]

        analysis = analyze_candidate(
            variable_name=variable_name,
            value=raw_value,
        )

        if not analysis[
            "is_suspicious"
        ]:
            continue

        findings.append(
            {
                "file": str(path),
                "line": line_number,
                "type": (
                    "Unknown Secret Candidate"
                ),
                "severity": "MEDIUM",
                "masked_value": mask_secret(
                    raw_value
                ),
                "candidate_score": analysis[
                    "score"
                ],
                "framework": None,
                "reasons": analysis[
                    "reasons"
                ],
            }
        )

    return findings


def scan_path(
    root: Path,
) -> tuple[int, list[dict]]:
    """
    Scan supported files inside a project directory.

    .leakguardignore is loaded from the exact
    directory being scanned.

    This means scanning the repository root can
    ignore demo_project/, while explicitly running:

        leakguard scan demo_project

    still scans the demo because the parent ignore
    file is not automatically inherited.
    """

    root = root.resolve()

    ignore_patterns = load_ignore_patterns(
        root
    )

    files_scanned = 0
    findings = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if should_skip(
            path=path,
            root=root,
            ignore_patterns=ignore_patterns,
        ):
            continue

        if not is_supported_file(
            path
        ):
            continue

        files_scanned += 1

        findings.extend(
            scan_file(path)
        )

    return files_scanned, findings