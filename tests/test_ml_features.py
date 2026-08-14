from leakguard.ml.features import (
    calculate_digit_ratio,
    calculate_special_ratio,
    calculate_uppercase_ratio,
    extract_ml_features,
)


def test_digit_ratio_for_numeric_value():
    ratio = calculate_digit_ratio(
        "123456"
    )

    assert ratio == 1.0


def test_digit_ratio_for_empty_value():
    ratio = calculate_digit_ratio(
        ""
    )

    assert ratio == 0.0


def test_uppercase_ratio():
    ratio = calculate_uppercase_ratio(
        "AAaa"
    )

    assert ratio == 0.5


def test_special_character_ratio():
    ratio = calculate_special_ratio(
        "ABC-123"
    )

    assert round(
        ratio,
        3,
    ) == 0.143


def test_extract_features_for_secret_like_value():
    features = extract_ml_features(
        variable_name="api_key",
        value="K7mP2xQ9vL4sN8zA1c",
    )

    assert features["length"] == 18

    assert features[
        "entropy"
    ] > 3.0

    assert features[
        "has_sensitive_name"
    ] == 1

    assert features[
        "is_compact"
    ] == 1

    assert features[
        "has_character_variety"
    ] == 1


def test_extract_features_for_ui_text():
    features = extract_ml_features(
        variable_name="message",
        value="Please enter your password",
    )

    assert features[
        "has_sensitive_name"
    ] == 0

    assert features[
        "is_compact"
    ] == 0