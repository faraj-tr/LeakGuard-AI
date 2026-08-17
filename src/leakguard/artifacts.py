from dataclasses import (
    dataclass,
    field,
)
from pathlib import Path

from leakguard.candidate import (
    analyze_candidate,
    has_sensitive_name,
)
from leakguard.dotenv import (
    extract_dotenv_assignment,
)
from leakguard.masking import mask_secret
from leakguard.scan_safety import (
    build_scan_limitation_finding,
    evaluate_content_bytes,
    evaluate_file_size,
)


ARTIFACT_DIRECTORIES = (
    Path("dist"),
    Path("build"),
    Path(".next") / "static",
)


def is_artifact_path(
    path: Path,
    root: Path,
) -> bool:
    """
    Return whether a project path belongs to
    one of LeakGuard's dedicated build-output
    scanning roots.

    Matching is lexical and project-relative;
    symbolic links are not resolved here.
    """

    try:
        relative_path = (
            path.relative_to(
                root
            )
        )

    except ValueError:
        return False

    parts = relative_path.parts

    if not parts:
        return False

    if parts[0] in {
        "dist",
        "build",
    }:
        return True

    return (
        len(parts) >= 2
        and parts[0] == ".next"
        and parts[1] == "static"
    )


ARTIFACT_EXTENSIONS = {
    ".js",
    ".mjs",
    ".cjs",
    ".css",
    ".html",
    ".json",
    ".map",
    ".txt",
}


DOTENV_SOURCE_FILES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
}


MIN_PROPAGATED_SECRET_LENGTH = 8


@dataclass(frozen=True)
class SecretInventoryItem:
    """
    One secret-like local environment value
    eligible for artifact propagation checks.

    raw_value is deliberately excluded from
    repr() so accidental logging of the
    inventory does not expose the secret.
    """

    source_file: Path
    variable_name: str
    candidate_score: int
    reasons: tuple[str, ...]

    raw_value: str = field(
        repr=False,
    )


def is_supported_artifact_file(
    path: Path,
) -> bool:
    """
    Return whether a build artifact has a
    supported text-oriented file extension.
    """

    return (
        path.suffix.lower()
        in ARTIFACT_EXTENSIONS
    )


def discover_artifact_files(
    root: Path,
) -> list[Path]:
    """
    Discover supported files under known
    application build-output directories.

    Discovery is deterministic.
    """

    root = root.resolve()

    discovered: set[Path] = set()

    for relative_directory in (
        ARTIFACT_DIRECTORIES
    ):
        artifact_root = (
            root
            / relative_directory
        )

        if not artifact_root.is_dir():
            continue

        for path in artifact_root.rglob(
            "*"
        ):
            if not path.is_file():
                continue

            if not is_supported_artifact_file(
                path
            ):
                continue

            discovered.add(
                path
            )

    return sorted(
        discovered,
        key=lambda path: (
            path
            .relative_to(root)
            .as_posix()
        ),
    )


def discover_dotenv_sources(
    root: Path,
) -> list[Path]:
    """
    Discover supported dotenv files anywhere
    inside the project while excluding common
    dependency/internal directories.

    This supports ordinary projects and simple
    monorepo layouts.
    """

    root = root.resolve()

    skipped_directories = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
    }

    discovered = []

    for path in root.rglob("*"):
        try:
            relative_path = (
                path.relative_to(
                    root
                )
            )

        except ValueError:
            continue

        if any(
            part in skipped_directories
            for part in relative_path.parts
        ):
            continue

        if (
            path.name
            not in DOTENV_SOURCE_FILES
        ):
            continue

        if not path.is_file():
            continue

        discovered.append(
            path
        )

    return sorted(
        discovered,
        key=lambda path: (
            path
            .relative_to(root)
            .as_posix()
        ),
    )


def _read_safe_text(
    path: Path,
) -> tuple[str | None, dict | None]:
    """
    Read one text file using LeakGuard's
    existing bounded-size and binary safety
    policy.

    On incomplete coverage, return a
    fail-closed finding instead of silently
    skipping the file.
    """

    try:
        size_bytes = (
            path.stat().st_size
        )

    except OSError:
        return (
            None,
            build_scan_limitation_finding(
                path=path,
                reason=(
                    "File metadata could not "
                    "be read safely during "
                    "artifact analysis."
                ),
            ),
        )

    size_result = evaluate_file_size(
        size_bytes
    )

    if not size_result.safe_to_scan:
        return (
            None,
            build_scan_limitation_finding(
                path=path,
                reason=(
                    size_result.reason
                    or (
                        "File size could not "
                        "be validated safely."
                    )
                ),
            ),
        )

    try:
        content_bytes = (
            path.read_bytes()
        )

    except OSError:
        return (
            None,
            build_scan_limitation_finding(
                path=path,
                reason=(
                    "File content could not "
                    "be read safely during "
                    "artifact analysis."
                ),
            ),
        )

    content_result = (
        evaluate_content_bytes(
            content_bytes
        )
    )

    if not content_result.safe_to_scan:
        return (
            None,
            build_scan_limitation_finding(
                path=path,
                reason=(
                    content_result.reason
                    or (
                        "File content could not "
                        "be validated safely."
                    )
                ),
            ),
        )

    return (
        content_bytes.decode(
            "utf-8-sig",
            errors="ignore",
        ),
        None,
    )


def collect_dotenv_secret_inventory(
    root: Path,
) -> tuple[
    list[SecretInventoryItem],
    list[dict],
]:
    """
    Build an in-memory inventory of secret-like
    dotenv values.

    A value is eligible when:
    - its variable name is security-sensitive,
      or
    - the existing deterministic candidate
      heuristic marks it suspicious.

    Very short values are excluded from exact
    substring propagation matching to limit
    accidental artifact false positives.

    Raw values never enter findings.
    """

    root = root.resolve()

    inventory = []
    limitations = []

    seen_raw_values: set[str] = set()

    for source_file in (
        discover_dotenv_sources(
            root
        )
    ):
        content, limitation = (
            _read_safe_text(
                source_file
            )
        )

        if limitation is not None:
            limitations.append(
                limitation
            )
            continue

        assert content is not None

        for line in content.splitlines():
            assignment = (
                extract_dotenv_assignment(
                    line
                )
            )

            if assignment is None:
                continue

            variable_name = assignment[
                "variable_name"
            ]

            raw_value = assignment[
                "value"
            ]

            if not raw_value:
                continue

            if (
                len(raw_value)
                < MIN_PROPAGATED_SECRET_LENGTH
            ):
                continue

            analysis = analyze_candidate(
                variable_name=variable_name,
                value=raw_value,
            )

            sensitive_name = (
                has_sensitive_name(
                    variable_name
                )
            )

            if not (
                sensitive_name
                or analysis[
                    "is_suspicious"
                ]
            ):
                continue

            if raw_value in seen_raw_values:
                continue

            seen_raw_values.add(
                raw_value
            )

            reasons = list(
                analysis[
                    "reasons"
                ]
            )

            if (
                sensitive_name
                and (
                    "Sensitive variable name"
                    not in reasons
                )
            ):
                reasons.insert(
                    0,
                    "Sensitive variable name",
                )

            inventory.append(
                SecretInventoryItem(
                    source_file=(
                        source_file
                    ),
                    variable_name=(
                        variable_name
                    ),
                    candidate_score=(
                        analysis[
                            "score"
                        ]
                    ),
                    reasons=tuple(
                        reasons
                    ),
                    raw_value=raw_value,
                )
            )

    return (
        inventory,
        limitations,
    )


def _find_line_number(
    content: str,
    start_index: int,
) -> int:
    """
    Convert a character offset into a
    one-based source line number.
    """

    return (
        content.count(
            "\n",
            0,
            start_index,
        )
        + 1
    )


def build_artifact_exposure_finding(
    artifact_path: Path,
    content: str,
    secret: SecretInventoryItem,
) -> dict | None:
    """
    Build one deterministic finding when a
    known local secret-like value appears
    verbatim inside a shipped artifact.
    """

    start_index = content.find(
        secret.raw_value
    )

    if start_index < 0:
        return None

    try:
        source_display = (
            secret.source_file.name
        )

    except OSError:
        source_display = str(
            secret.source_file
        )

    return {
        "file": str(
            artifact_path
        ),
        "line": _find_line_number(
            content,
            start_index,
        ),
        "type": (
            "Artifact Secret Exposure"
        ),
        "severity": "CRITICAL",
        "masked_value": mask_secret(
            secret.raw_value
        ),
        "candidate_score": (
            secret.candidate_score
        ),
        "framework": "Artifact",
        "reasons": [
            (
                "Secret-like environment "
                "value was propagated into "
                "a shipped build artifact."
            ),
            (
                "Source variable: "
                f"{secret.variable_name}"
            ),
            (
                "Source file: "
                f"{source_display}"
            ),
        ],
    }


def scan_artifact_content(
    path: Path,
    content: str,
    inventory: list[
        SecretInventoryItem
    ],
) -> list[dict]:
    """
    Compare artifact text against the local
    secret inventory.

    Each distinct inventory value produces at
    most one finding per artifact even if the
    value appears multiple times.
    """

    findings = []

    for secret in inventory:
        finding = (
            build_artifact_exposure_finding(
                artifact_path=path,
                content=content,
                secret=secret,
            )
        )

        if finding is None:
            continue

        findings.append(
            finding
        )

    return findings


def scan_artifacts(
    root: Path,
) -> tuple[int, list[dict]]:
    """
    Scan known build-output directories for
    exact propagation of local dotenv secrets.

    Candidate v2 ML is intentionally not used
    here. Artifact propagation evidence is
    deterministic.
    """

    root = root.resolve()

    inventory, findings = (
        collect_dotenv_secret_inventory(
            root
        )
    )

    artifact_files = (
        discover_artifact_files(
            root
        )
    )

    files_scanned = 0

    for artifact_path in artifact_files:
        files_scanned += 1

        content, limitation = (
            _read_safe_text(
                artifact_path
            )
        )

        if limitation is not None:
            findings.append(
                limitation
            )
            continue

        assert content is not None

        findings.extend(
            scan_artifact_content(
                path=artifact_path,
                content=content,
                inventory=inventory,
            )
        )

    return (
        files_scanned,
        findings,
    )
