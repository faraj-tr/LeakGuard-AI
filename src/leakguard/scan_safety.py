from dataclasses import dataclass
from pathlib import Path


MAX_SCANNABLE_FILE_BYTES = (
    2 * 1024 * 1024
)

BINARY_SAMPLE_BYTES = 8192


@dataclass(frozen=True)
class ScanSafetyResult:
    """
    Result of evaluating whether file content
    can be safely passed to the text scanner.
    """

    safe_to_scan: bool
    reason: str | None


def evaluate_file_size(
    size_bytes: int,
) -> ScanSafetyResult:
    """
    Reject files that exceed the bounded
    source-scanning size limit.

    This protects LeakGuard from loading
    arbitrarily large supported-looking files
    into memory.
    """

    if size_bytes < 0:
        return ScanSafetyResult(
            safe_to_scan=False,
            reason=(
                "File size could not be "
                "validated safely."
            ),
        )

    if (
        size_bytes
        > MAX_SCANNABLE_FILE_BYTES
    ):
        return ScanSafetyResult(
            safe_to_scan=False,
            reason=(
                "File exceeds the safe "
                "source scan limit of "
                f"{MAX_SCANNABLE_FILE_BYTES} "
                "bytes."
            ),
        )

    return ScanSafetyResult(
        safe_to_scan=True,
        reason=None,
    )


def is_probably_binary(
    content: bytes,
) -> bool:
    """
    Detect strong evidence of binary content.

    A NUL byte is treated conservatively as
    binary evidence because supported LeakGuard
    source/config formats are expected to be
    text.

    Only a bounded prefix is inspected.
    """

    sample = content[
        :BINARY_SAMPLE_BYTES
    ]

    return b"\x00" in sample


def evaluate_content_bytes(
    content: bytes,
) -> ScanSafetyResult:
    """
    Apply bounded-size and binary checks to
    content that has already been read.

    The size check is repeated here as
    defense-in-depth against file changes
    between stat() and read().
    """

    size_result = evaluate_file_size(
        len(
            content
        )
    )

    if not size_result.safe_to_scan:
        return size_result

    if is_probably_binary(
        content
    ):
        return ScanSafetyResult(
            safe_to_scan=False,
            reason=(
                "Binary content was detected "
                "in a supported text file."
            ),
        )

    return ScanSafetyResult(
        safe_to_scan=True,
        reason=None,
    )


def build_scan_limitation_finding(
    path: Path,
    reason: str,
) -> dict:
    """
    Build a fail-closed coverage finding.

    This represents a scanner coverage
    limitation, not evidence that a credential
    itself was found.
    """

    return {
        "file": str(
            path
        ),
        "line": 1,
        "type": (
            "Scan Coverage Limitation"
        ),
        "severity": "MEDIUM",
        "masked_value": "-",
        "candidate_score": None,
        "framework": None,
        "reasons": [
            reason
        ],
    }
