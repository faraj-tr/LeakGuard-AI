import re

from leakguard.ml.features import (
    extract_ml_features,
)


UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


HEX_PATTERN = re.compile(
    r"^[0-9a-fA-F]+$"
)


BASE64URL_SEGMENT_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]+$"
)


PUBLIC_FRONTEND_PREFIXES = (
    "VITE_",
    "NEXT_PUBLIC_",
)


IDENTIFIER_NAME_HINTS = (
    "id",
    "identifier",
    "uuid",
    "ref",
    "reference",
    "request",
    "trace",
    "build",
    "commit",
    "checksum",
    "digest",
)


PLACEHOLDER_HINTS = (
    "example",
    "placeholder",
    "replace",
    "redacted",
    "not-configured",
    "not_configured",
    "fake",
    "demo",
    "sample",
    "your-",
    "your_",
    "insert_",
    "insert-",
    "do-not-use",
    "do_not_use",
)


REFERENCE_PREFIXES = (
    "${",
    "$env:",
    "process.env.",
    "env.",
    "vault://",
)


def normalize_name(
    variable_name: str,
) -> str:
    """
    Normalize variable names for contextual
    feature extraction.
    """

    return (
        variable_name
        .strip()
        .lower()
    )


def normalize_value(
    value: str,
) -> str:
    """
    Normalize values without destroying
    their original structural signals.
    """

    return value.strip()


def looks_like_uuid(
    value: str,
) -> int:
    """
    Detect a canonical UUID.

    UUIDs are common high-entropy safe
    identifiers and were a known source of
    false positives during development.
    """

    normalized = normalize_value(
        value
    )

    return int(
        bool(
            UUID_PATTERN.fullmatch(
                normalized
            )
        )
    )


def looks_like_fixed_hash(
    value: str,
) -> int:
    """
    Detect common fixed-length hexadecimal
    hashes seen in safe identifiers.

    Development errors included 40-character
    commit hashes and 64-character digests.
    """

    normalized = normalize_value(
        value
    )

    if len(normalized) not in {
        40,
        64,
    }:
        return 0

    return int(
        bool(
            HEX_PATTERN.fullmatch(
                normalized
            )
        )
    )


def is_hex_only(
    value: str,
) -> int:
    """
    Detect whether a reasonably long value
    consists only of hexadecimal characters.

    This is intentionally separate from
    looks_like_fixed_hash because hexadecimal
    secrets may also exist.
    """

    normalized = normalize_value(
        value
    )

    if len(normalized) < 16:
        return 0

    return int(
        bool(
            HEX_PATTERN.fullmatch(
                normalized
            )
        )
    )


def looks_like_reference(
    value: str,
) -> int:
    """
    Detect values that reference a secret
    stored somewhere else instead of
    containing the secret itself.
    """

    normalized = normalize_value(
        value
    )

    lowered = normalized.lower()

    if any(
        lowered.startswith(
            prefix.lower()
        )
        for prefix in REFERENCE_PREFIXES
    ):
        return 1

    if (
        normalized.startswith("%")
        and normalized.endswith("%")
        and len(normalized) > 2
    ):
        return 1

    if lowered.startswith(
        "os.getenv("
    ):
        return 1

    return 0


def looks_like_placeholder(
    value: str,
) -> int:
    """
    Detect documentation, example,
    redacted, and placeholder values.
    """

    lowered = normalize_value(
        value
    ).lower()

    return int(
        any(
            hint in lowered
            for hint in PLACEHOLDER_HINTS
        )
    )


def has_public_frontend_prefix(
    variable_name: str,
) -> int:
    """
    Detect frontend-public configuration
    prefixes known during development.
    """

    normalized = (
        variable_name
        .strip()
        .upper()
    )

    return int(
        normalized.startswith(
            PUBLIC_FRONTEND_PREFIXES
        )
    )


def has_identifier_name(
    variable_name: str,
) -> int:
    """
    Detect names suggesting identifiers,
    hashes, references, or build metadata.

    This feature does not automatically
    mark a value as safe.
    """

    normalized = normalize_name(
        variable_name
    )

    tokens = [
        token
        for token in re.split(
            r"[^a-z0-9]+",
            normalized,
        )
        if token
    ]

    return int(
        any(
            token in IDENTIFIER_NAME_HINTS
            for token in tokens
        )
    )


def looks_like_jwt(
    value: str,
) -> int:
    """
    Detect a JWT-like three-segment value.

    This is structural detection only and
    does not validate or decode the token.
    """

    normalized = normalize_value(
        value
    )

    parts = normalized.split(
        "."
    )

    if len(parts) != 3:
        return 0

    if any(
        len(part) < 6
        for part in parts
    ):
        return 0

    return int(
        all(
            BASE64URL_SEGMENT_PATTERN.fullmatch(
                part
            )
            is not None
            for part in parts
        )
    )


def looks_like_passphrase(
    value: str,
) -> int:
    """
    Detect a multi-word passphrase-like
    structure.

    This intentionally uses only generic
    structure and not any final benchmark
    templates.
    """

    normalized = normalize_value(
        value
    )

    if "://" in normalized:
        return 0

    words = [
        item
        for item in re.split(
            r"[\s.-]+",
            normalized,
        )
        if item
    ]

    if not 4 <= len(words) <= 8:
        return 0

    if not all(
        word.isalpha()
        and len(word) >= 3
        for word in words
    ):
        return 0

    return 1


def extract_context_features(
    variable_name: str,
    value: str,
) -> dict:
    """
    Extract Candidate v2 contextual
    security features.

    These features supplement the original
    numerical feature set. They are derived
    only from variable name and candidate
    value, never from labels or sample_type.
    """

    original_features = (
        extract_ml_features(
            variable_name=variable_name,
            value=value,
        )
    )

    context_features = {
        "looks_like_uuid": (
            looks_like_uuid(
                value
            )
        ),
        "looks_like_fixed_hash": (
            looks_like_fixed_hash(
                value
            )
        ),
        "is_hex_only": (
            is_hex_only(
                value
            )
        ),
        "looks_like_reference": (
            looks_like_reference(
                value
            )
        ),
        "looks_like_placeholder": (
            looks_like_placeholder(
                value
            )
        ),
        "has_public_frontend_prefix": (
            has_public_frontend_prefix(
                variable_name
            )
        ),
        "has_identifier_name": (
            has_identifier_name(
                variable_name
            )
        ),
        "looks_like_jwt": (
            looks_like_jwt(
                value
            )
        ),
        "looks_like_passphrase": (
            looks_like_passphrase(
                value
            )
        ),
    }

    return {
        **original_features,
        **context_features,
    }
