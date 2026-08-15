from leakguard.ml.context_features import (
    extract_context_features,
    has_identifier_name,
    has_public_frontend_prefix,
    is_hex_only,
    looks_like_fixed_hash,
    looks_like_jwt,
    looks_like_passphrase,
    looks_like_placeholder,
    looks_like_reference,
    looks_like_uuid,
)


def test_uuid_is_detected():
    assert (
        looks_like_uuid(
            "123e4567-e89b-12d3-a456-426614174000"
        )
        == 1
    )


def test_normal_value_is_not_uuid():
    assert (
        looks_like_uuid(
            "normal-application-value"
        )
        == 0
    )


def test_fixed_hash_is_detected():
    value = (
        "a" * 40
    )

    assert (
        looks_like_fixed_hash(
            value
        )
        == 1
    )


def test_long_hex_value_is_detected():
    assert (
        is_hex_only(
            "a1b2c3d4e5f60718"
        )
        == 1
    )


def test_environment_reference_is_detected():
    assert (
        looks_like_reference(
            "${SECRET_FROM_VAULT}"
        )
        == 1
    )

    assert (
        looks_like_reference(
            "$env:API_KEY"
        )
        == 1
    )


def test_placeholder_is_detected():
    assert (
        looks_like_placeholder(
            "EXAMPLE_ONLY_DO_NOT_USE"
        )
        == 1
    )


def test_public_frontend_prefix_is_detected():
    assert (
        has_public_frontend_prefix(
            "VITE_RELEASE_CHANNEL"
        )
        == 1
    )

    assert (
        has_public_frontend_prefix(
            "NEXT_PUBLIC_DOCS_HOST"
        )
        == 1
    )


def test_identifier_name_is_detected():
    assert (
        has_identifier_name(
            "request_id"
        )
        == 1
    )

    assert (
        has_identifier_name(
            "build_digest"
        )
        == 1
    )


def test_jwt_like_value_is_detected():
    value = (
        "abcdefghi."
        "ABCDEFGHIJKLM."
        "0123456789_-abc"
    )

    assert (
        looks_like_jwt(
            value
        )
        == 1
    )


def test_passphrase_is_detected():
    assert (
        looks_like_passphrase(
            "amber-harbor-meteor-lantern-canyon"
        )
        == 1
    )


def test_context_features_include_old_and_new_features():
    features = (
        extract_context_features(
            variable_name="request_id",
            value=(
                "123e4567-e89b-12d3-"
                "a456-426614174000"
            ),
        )
    )

    assert (
        "entropy"
        in features
    )

    assert (
        "has_sensitive_name"
        in features
    )

    assert (
        "looks_like_uuid"
        in features
    )

    assert (
        "has_identifier_name"
        in features
    )

    assert (
        features[
            "looks_like_uuid"
        ]
        == 1
    )

    assert (
        features[
            "has_identifier_name"
        ]
        == 1
    )
