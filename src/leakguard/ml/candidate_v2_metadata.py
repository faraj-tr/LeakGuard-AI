import re

from leakguard.ml.context_features import (
    extract_context_features,
)


SAFE_HASH_METADATA_TOKENS = {
    "commit",
    "revision",
    "checksum",
    "digest",
    "sha",
    "fingerprint",
    "etag",
    "repository",
    "source",
}


def tokenize_variable_name(
    variable_name: str,
) -> set[str]:
    """
    Normalize a variable name into semantic
    lowercase tokens.
    """

    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        variable_name.lower(),
    )

    return {
        token
        for token in normalized.split("_")
        if token
    }


def looks_like_safe_hash_metadata(
    variable_name: str,
    value: str,
) -> int:
    """
    Detect fixed-length hashes that appear
    to represent revision/artifact metadata.

    This is a Candidate v2 model feature,
    not a deterministic allow rule.

    Sensitive variable names deliberately
    suppress the feature so values such as
    password_hash are not automatically
    treated as safe.
    """

    context = extract_context_features(
        variable_name=variable_name,
        value=value,
    )

    if not context[
        "looks_like_fixed_hash"
    ]:
        return 0

    if context[
        "has_sensitive_name"
    ]:
        return 0

    tokens = tokenize_variable_name(
        variable_name
    )

    has_metadata_token = bool(
        tokens
        & SAFE_HASH_METADATA_TOKENS
    )

    return int(
        has_metadata_token
    )
