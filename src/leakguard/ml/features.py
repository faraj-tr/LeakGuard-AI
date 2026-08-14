from leakguard.candidate import (
    has_character_variety,
    has_sensitive_name,
    is_compact_value,
)
from leakguard.entropy import calculate_entropy


def calculate_digit_ratio(value: str) -> float:
    """
    Calculate the percentage of characters
    in a value that are digits.
    """

    if not value:
        return 0.0

    digit_count = sum(
        character.isdigit()
        for character in value
    )

    return digit_count / len(value)


def calculate_uppercase_ratio(value: str) -> float:
    """
    Calculate the percentage of characters
    that are uppercase letters.
    """

    if not value:
        return 0.0

    uppercase_count = sum(
        character.isupper()
        for character in value
    )

    return uppercase_count / len(value)


def calculate_special_ratio(value: str) -> float:
    """
    Calculate the percentage of characters
    that are neither letters nor digits.
    """

    if not value:
        return 0.0

    special_count = sum(
        not character.isalnum()
        for character in value
    )

    return special_count / len(value)


def extract_ml_features(
    variable_name: str,
    value: str,
) -> dict:
    """
    Convert a candidate into numerical and
    boolean features suitable for machine learning.
    """

    return {
        "length": len(value),

        "entropy": round(
            calculate_entropy(value),
            6,
        ),

        "digit_ratio": round(
            calculate_digit_ratio(value),
            6,
        ),

        "uppercase_ratio": round(
            calculate_uppercase_ratio(value),
            6,
        ),

        "special_ratio": round(
            calculate_special_ratio(value),
            6,
        ),

        "has_sensitive_name": int(
            has_sensitive_name(
                variable_name
            )
        ),

        "is_compact": int(
            is_compact_value(value)
        ),

        "has_character_variety": int(
            has_character_variety(value)
        ),
    }