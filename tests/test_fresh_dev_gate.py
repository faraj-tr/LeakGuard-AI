import pandas as pd
import pytest

from leakguard.ml.dataset_separation import (
    sha256_file,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_DEVELOPMENT_SHA256,
    EXPECTED_TRAINING_SHA256,
    validate_frozen_dataset,
)


def create_dataset_file(
    tmp_path,
    source="test_source",
):
    dataframe = pd.DataFrame(
        {
            "variable_name": [
                "value_a",
                "value_b",
            ],
            "value": [
                "alpha",
                "beta",
            ],
            "label": [
                0,
                1,
            ],
            "sample_type": [
                "safe_test",
                "secret_test",
            ],
            "source": [
                source,
                source,
            ],
        }
    )

    path = (
        tmp_path
        / "dataset.csv"
    )

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )

    return path


def test_frozen_hash_constants_are_sha256_length():
    assert len(
        EXPECTED_TRAINING_SHA256
    ) == 64

    assert len(
        EXPECTED_DEVELOPMENT_SHA256
    ) == 64


def test_validate_frozen_dataset_accepts_valid_file(
    tmp_path,
):
    path = create_dataset_file(
        tmp_path
    )

    digest = sha256_file(
        path
    )

    dataframe = (
        validate_frozen_dataset(
            path=path,
            expected_sha256=digest,
            expected_samples=2,
            expected_source="test_source",
            expected_label_counts={
                0: 1,
                1: 1,
            },
        )
    )

    assert len(dataframe) == 2


def test_validate_frozen_dataset_rejects_hash_mismatch(
    tmp_path,
):
    path = create_dataset_file(
        tmp_path
    )

    with pytest.raises(
        ValueError
    ):
        validate_frozen_dataset(
            path=path,
            expected_sha256=(
                "0" * 64
            ),
            expected_samples=2,
            expected_source="test_source",
            expected_label_counts={
                0: 1,
                1: 1,
            },
        )


def test_validate_frozen_dataset_rejects_source_mismatch(
    tmp_path,
):
    path = create_dataset_file(
        tmp_path
    )

    digest = sha256_file(
        path
    )

    with pytest.raises(
        ValueError
    ):
        validate_frozen_dataset(
            path=path,
            expected_sha256=digest,
            expected_samples=2,
            expected_source=(
                "unexpected_source"
            ),
            expected_label_counts={
                0: 1,
                1: 1,
            },
        )


def test_validate_frozen_dataset_rejects_label_distribution(
    tmp_path,
):
    path = create_dataset_file(
        tmp_path
    )

    digest = sha256_file(
        path
    )

    with pytest.raises(
        ValueError
    ):
        validate_frozen_dataset(
            path=path,
            expected_sha256=digest,
            expected_samples=2,
            expected_source="test_source",
            expected_label_counts={
                0: 2,
                1: 0,
            },
        )
