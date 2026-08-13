from leakguard.entropy import calculate_entropy


SENSITIVE_KEYWORDS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "client_secret",
    "access_key",
    "credential",
    "credentials",
}


def has_sensitive_name(variable_name: str) -> bool:
    """
    Check whether a variable name contains
    security-sensitive terminology.
    """

    normalized_name = (
        variable_name
        .lower()
        .replace("-", "_")
    )

    return any(
        keyword in normalized_name
        for keyword in SENSITIVE_KEYWORDS
    )


def has_character_variety(value: str) -> bool:
    """
    Check whether a value mixes multiple
    character categories.
    """

    has_lower = any(char.islower() for char in value)
    has_upper = any(char.isupper() for char in value)
    has_digit = any(char.isdigit() for char in value)

    categories = sum(
        [
            has_lower,
            has_upper,
            has_digit,
        ]
    )

    return categories >= 2


def is_compact_value(value: str) -> bool:
    """
    Secret-like values are often compact strings
    rather than natural-language sentences.
    """

    return not any(
        char.isspace()
        for char in value
    )


def analyze_candidate(
    variable_name: str,
    value: str,
) -> dict:
    """
    Analyze a possible secret using multiple signals.

    This does not prove that a value is a real secret.
    It only calculates a suspicion score.
    """

    score = 0
    reasons = []

    entropy = calculate_entropy(value)

    sensitive_name = has_sensitive_name(variable_name)
    compact_value = is_compact_value(value)

    # Signal 1:
    # Security-sensitive variable names are important context.
    if sensitive_name:
        score += 40
        reasons.append("Sensitive variable name")

    # Signal 2:
    # Long values become interesting when they are compact,
    # or when the variable name itself is security-sensitive.
    if len(value) >= 16 and (
        compact_value or sensitive_name
    ):
        score += 20
        reasons.append("Long secret-like value")

    # Signal 3:
    # Entropy is useful mainly for compact token-like strings.
    if entropy >= 3.5 and compact_value:
        score += 25
        reasons.append("High entropy")

    # Signal 4:
    # Mixed character categories are more meaningful
    # for compact values than natural-language sentences.
    if (
        has_character_variety(value)
        and compact_value
    ):
        score += 15
        reasons.append("Character variety")

    score = min(score, 100)

    return {
        "variable_name": variable_name,
        "length": len(value),
        "entropy": round(entropy, 3),
        "score": score,
        "is_suspicious": score >= 50,
        "reasons": reasons,
    }