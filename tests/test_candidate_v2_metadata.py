from leakguard.ml.candidate_v2_metadata import (
    looks_like_safe_hash_metadata,
    tokenize_variable_name,
)


HASH_40 = (
    "0123456789abcdef"
    "0123456789abcdef"
    "01234567"
)


def test_metadata_tokenizer_normalizes_names():
    tokens = tokenize_variable_name(
        "Repository-Source_Hash"
    )

    assert {
        "repository",
        "source",
        "hash",
    }.issubset(
        tokens
    )


def test_repository_hash_is_safe_metadata_candidate():
    result = (
        looks_like_safe_hash_metadata(
            variable_name=(
                "repository_hash"
            ),
            value=HASH_40,
        )
    )

    assert result == 1


def test_source_revision_is_safe_metadata_candidate():
    result = (
        looks_like_safe_hash_metadata(
            variable_name=(
                "source_revision"
            ),
            value=HASH_40,
        )
    )

    assert result == 1


def test_commit_sha_is_safe_metadata_candidate():
    result = (
        looks_like_safe_hash_metadata(
            variable_name="commit_sha",
            value=HASH_40,
        )
    )

    assert result == 1


def test_sensitive_hash_name_is_not_safe_metadata():
    result = (
        looks_like_safe_hash_metadata(
            variable_name=(
                "password_hash"
            ),
            value=HASH_40,
        )
    )

    assert result == 0


def test_non_fixed_hash_is_not_safe_metadata():
    result = (
        looks_like_safe_hash_metadata(
            variable_name=(
                "repository_hash"
            ),
            value="abc123",
        )
    )

    assert result == 0
