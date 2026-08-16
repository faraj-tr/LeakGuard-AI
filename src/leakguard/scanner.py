from pathlib import Path
from typing import Any

from leakguard.candidate import analyze_candidate
from leakguard.client_exposure import analyze_client_exposure
from leakguard.dotenv import extract_dotenv_assignment
from leakguard.extractor import (
    classify_assignment,
    extract_assignment,
)
from leakguard.ignore import (
    get_project_relative_path,
    is_ignored,
    load_ignore_patterns,
)
from leakguard.masking import mask_secret
from leakguard.patterns import (
    ASSIGNMENT_SECRET_PATTERNS,
    INLINE_SECRET_PATTERNS,
    matches_assignment_secret,
)
from leakguard.scan_safety import (
    build_scan_limitation_finding,
    evaluate_content_bytes,
    evaluate_file_size,
)


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


SUPPORTED_EXTENSIONS = {
    *CODE_EXTENSIONS,
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


def is_code_file(path: Path) -> bool:
    """
    Return whether a file uses code assignment
    semantics that require literal/expression
    separation.
    """

    return (
        path.suffix.lower()
        in CODE_EXTENSIONS
    )


def is_dotenv_file(path: Path) -> bool:
    """
    Check whether a file is a supported
    environment configuration file.
    """

    return path.name in SPECIAL_FILES


def should_skip(
    path: Path,
    root: Path,
    ignore_patterns: list[str],
) -> bool:
    """
    Check whether a project path should be
    skipped.

    Built-in skipped directory names are
    evaluated only relative to the scan root.

    Paths outside the scan root are never
    scanned.
    """

    relative_path = (
        get_project_relative_path(
            path=path,
            root=root,
        )
    )

    if relative_path is None:
        return True

    if any(
        part in SKIP_DIRECTORIES
        for part in relative_path.parts
    ):
        return True

    return is_ignored(
        path=path,
        root=root,
        patterns=ignore_patterns,
    )

def score_ml_advisory(
    ml_advisory_runtime: Any | None,
    variable_name: str,
    raw_value: str,
) -> dict | None:
    """
    Request an advisory ML score when a
    runtime has explicitly been supplied.

    Raw values exist only during this call
    and are never copied into the finding.
    """

    if ml_advisory_runtime is None:
        return None

    return ml_advisory_runtime.score(
        variable_name=variable_name,
        value=raw_value,
    )


def build_known_secret_finding(
    path: Path,
    line_number: int,
    detector: dict,
    raw_secret: str,
) -> dict:
    """
    Build a masked deterministic finding
    for a known secret detector.
    """

    return {
        "file": str(path),
        "line": line_number,
        "type": detector[
            "name"
        ],
        "severity": detector[
            "severity"
        ],
        "masked_value": (
            mask_secret(
                raw_secret
            )
        ),
        "candidate_score": None,
        "framework": None,
        "reasons": [],
    }


def scan_content(
    path: Path,
    content: str,
    ml_advisory_runtime: Any | None = None,
) -> list[dict]:
    """
    Scan source content without reading it
    directly from the working tree.

    This allows LeakGuard to scan both:
    - normal files
    - staged Git blobs

    Candidate v2 may optionally enrich
    generic findings with an advisory score.

    ML does not create, remove, suppress,
    or escalate deterministic findings.
    """

    # UTF-8 BOM may be emitted by Windows
    # editors or PowerShell. Normalize it
    # once at the content boundary so every
    # detection layer sees the real first
    # character while preserving line numbers.
    content = content.removeprefix(
        "\ufeff"
    )

    findings = []

    for line_number, line in enumerate(
        content.splitlines(),
        start=1,
    ):

        dotenv_assignment = None

        if is_dotenv_file(
            path
        ):
            dotenv_assignment = (
                extract_dotenv_assignment(
                    line
                )
            )

        code_assignment = None

        if is_code_file(
            path
        ):
            code_assignment = (
                classify_assignment(
                    line
                )
            )

        # =================================
        # Layer 1:
        # Client-side environment exposure
        # =================================

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

            exposure = (
                analyze_client_exposure(
                    variable_name=variable_name,
                    value=raw_value,
                )
            )

            if exposure[
                "is_risky"
            ]:

                findings.append(
                    {
                        "file": str(path),
                        "line": line_number,
                        "type": (
                            "Client-Side "
                            "Secret Exposure"
                        ),
                        "severity": exposure[
                            "severity"
                        ],
                        "masked_value": (
                            mask_secret(
                                raw_value
                            )
                        ),
                        "candidate_score": (
                            exposure[
                                "candidate_score"
                            ]
                        ),
                        "framework": exposure[
                            "framework"
                        ],
                        "reasons": exposure[
                            "reasons"
                        ],
                    }
                )

                continue

        # =================================
        # Layer 2A:
        # Assignment-based known secrets
        # =================================

        known_pattern_found = False

        if is_code_file(
            path
        ):

            # Security-sensitive assignment
            # detectors operate only on
            # supported fixed string literals.
            #
            # Expressions such as:
            #   password = generate_password()
            #   api_key = os.getenv("API_KEY")
            #
            # must never be interpreted as
            # hardcoded secret values.
            if (
                code_assignment is not None
                and code_assignment[
                    "kind"
                ]
                == "literal"
            ):

                variable_name = (
                    code_assignment[
                        "variable_name"
                    ]
                )

                raw_value = (
                    code_assignment[
                        "value"
                    ]
                )

                for detector in (
                    ASSIGNMENT_SECRET_PATTERNS
                ):

                    if not (
                        matches_assignment_secret(
                            detector=detector,
                            variable_name=(
                                variable_name
                            ),
                            value=raw_value,
                        )
                    ):
                        continue

                    findings.append(
                        build_known_secret_finding(
                            path=path,
                            line_number=(
                                line_number
                            ),
                            detector=detector,
                            raw_secret=(
                                raw_value
                            ),
                        )
                    )

                    known_pattern_found = True

        else:

            # Structured configuration formats
            # retain raw assignment matching.
            #
            # Expressions are not treated as
            # executable code in these formats,
            # and this preserves existing
            # YAML / JSON / dotenv coverage.
            for detector in (
                ASSIGNMENT_SECRET_PATTERNS
            ):

                for match in detector[
                    "pattern"
                ].finditer(
                    line
                ):

                    raw_secret = (
                        match.group(
                            "secret"
                        )
                    )

                    findings.append(
                        build_known_secret_finding(
                            path=path,
                            line_number=(
                                line_number
                            ),
                            detector=detector,
                            raw_secret=(
                                raw_secret
                            ),
                        )
                    )

                    known_pattern_found = True

        # =================================
        # Layer 2B:
        # Inline secret patterns
        # =================================

        seen_inline_secret_keys: set[
            tuple[str, str]
        ] = set()

        for detector in (
            INLINE_SECRET_PATTERNS
        ):

            for match in detector[
                "pattern"
            ].finditer(
                line
            ):

                raw_secret = match.group(
                    "secret"
                )

                secret_key = (
                    detector["name"],
                    raw_secret,
                )

                if (
                    secret_key
                    in seen_inline_secret_keys
                ):
                    continue

                seen_inline_secret_keys.add(
                    secret_key
                )

                findings.append(
                    build_known_secret_finding(
                        path=path,
                        line_number=(
                            line_number
                        ),
                        detector=detector,
                        raw_secret=(
                            raw_secret
                        ),
                    )
                )

                known_pattern_found = True

        if known_pattern_found:
            continue

        # =================================
        # Layer 3:
        # Generic heuristic candidate
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

        finding = {
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

        ml_advisory = score_ml_advisory(
            ml_advisory_runtime=(
                ml_advisory_runtime
            ),
            variable_name=variable_name,
            raw_value=raw_value,
        )

        if ml_advisory is not None:
            finding[
                "ml_advisory"
            ] = ml_advisory

        findings.append(
            finding
        )

    return findings


def scan_file(
    path: Path,
    ml_advisory_runtime: Any | None = None,
) -> list[dict]:
    """
    Read and scan one working-tree file.

    Symbolic links are not followed.

    Metadata/read failures and coverage
    limitations fail closed instead of
    disappearing silently.
    """

    try:
        is_symbolic_link = (
            path.is_symlink()
        )

    except OSError:
        return [
            build_scan_limitation_finding(
                path=path,
                reason=(
                    "File metadata could not "
                    "be inspected safely."
                ),
            )
        ]

    if is_symbolic_link:

        return [
            build_scan_limitation_finding(
                path=path,
                reason=(
                    "Symbolic links are not "
                    "followed during working-tree "
                    "security scans."
                ),
            )
        ]

    try:
        file_size = (
            path.stat()
            .st_size
        )

    except OSError:
        return [
            build_scan_limitation_finding(
                path=path,
                reason=(
                    "File metadata could not "
                    "be read safely."
                ),
            )
        ]

    size_result = evaluate_file_size(
        file_size
    )

    if not size_result.safe_to_scan:

        return [
            build_scan_limitation_finding(
                path=path,
                reason=(
                    size_result.reason
                    or "File could not be "
                    "scanned safely."
                ),
            )
        ]

    try:
        raw_content = (
            path.read_bytes()
        )

    except OSError:
        return [
            build_scan_limitation_finding(
                path=path,
                reason=(
                    "File content could not "
                    "be read safely."
                ),
            )
        ]

    content_result = (
        evaluate_content_bytes(
            raw_content
        )
    )

    if not content_result.safe_to_scan:

        return [
            build_scan_limitation_finding(
                path=path,
                reason=(
                    content_result.reason
                    or "File could not be "
                    "scanned safely."
                ),
            )
        ]

    content = raw_content.decode(
        "utf-8",
        errors="ignore",
    )

    return scan_content(
        path=path,
        content=content,
        ml_advisory_runtime=(
            ml_advisory_runtime
        ),
    )

def scan_path(
    root: Path,
    ml_advisory_runtime: Any | None = None,
) -> tuple[int, list[dict]]:
    """
    Scan supported files inside a project.

    Supported symbolic-link files are treated
    as fail-closed coverage limitations rather
    than being followed outside the project.

    A supplied ML advisory runtime is reused
    across every scanned file.
    """

    root = root.resolve()

    ignore_patterns = (
        load_ignore_patterns(
            root
        )
    )

    files_scanned = 0
    findings = []

    project_paths = sorted(
        root.rglob("*"),
        key=lambda candidate: (
            candidate
            .relative_to(root)
            .as_posix()
        ),
    )

    for path in project_paths:

        # Inspect symbolic-link metadata before
        # is_file(), because is_file() follows
        # the link target.
        #
        # Metadata failures during traversal
        # fail closed for supported project
        # paths rather than aborting the scan.
        try:
            is_symbolic_link = (
                path.is_symlink()
            )

        except OSError:

            if should_skip(
                path=path,
                root=root,
                ignore_patterns=(
                    ignore_patterns
                ),
            ):
                continue

            if not is_supported_file(
                path
            ):
                continue

            files_scanned += 1

            findings.append(
                build_scan_limitation_finding(
                    path=path,
                    reason=(
                        "File metadata could not "
                        "be inspected safely "
                        "during project traversal."
                    ),
                )
            )

            continue

        if is_symbolic_link:

            if should_skip(
                path=path,
                root=root,
                ignore_patterns=(
                    ignore_patterns
                ),
            ):
                continue

            if not is_supported_file(
                path
            ):
                continue

            files_scanned += 1

            findings.extend(
                scan_file(
                    path=path,
                    ml_advisory_runtime=(
                        ml_advisory_runtime
                    ),
                )
            )

            continue

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
            scan_file(
                path=path,
                ml_advisory_runtime=(
                    ml_advisory_runtime
                ),
            )
        )

    return (
        files_scanned,
        findings,
    )
