import pandas as pd
import pytest

from leakguard.ml.dataset import (
    generate_synthetic_dataset,
    save_synthetic_dataset,
)


def test_dataset_is_balanced():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=20,
            seed=42,
        )
    )

    counts = (
        dataframe[
            "label"
        ]
        .value_counts()
        .to_dict()
    )

    assert len(dataframe) == 40
    assert counts[0] == 20
    assert counts[1] == 20


def test_dataset_contains_required_columns():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=10,
            seed=42,
        )
    )

    required_columns = {
        "sample_id",
        "variable_name",
        "value",
        "label",
        "sample_type",
        "framework",
        "source",
        "length",
        "entropy",
        "digit_ratio",
        "uppercase_ratio",
        "special_ratio",
        "has_sensitive_name",
        "is_compact",
        "has_character_variety",
    }

    assert required_columns.issubset(
        set(
            dataframe.columns
        )
    )


def test_feature_ratios_are_valid():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=20,
            seed=42,
        )
    )

    ratio_columns = [
        "digit_ratio",
        "uppercase_ratio",
        "special_ratio",
    ]

    for column in ratio_columns:

        assert (
            dataframe[column]
            >= 0.0
        ).all()

        assert (
            dataframe[column]
            <= 1.0
        ).all()


def test_dataset_generation_is_reproducible():
    first = (
        generate_synthetic_dataset(
            samples_per_class=15,
            seed=123,
        )
    )

    second = (
        generate_synthetic_dataset(
            samples_per_class=15,
            seed=123,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_dataset_contains_hard_examples():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=50,
            seed=42,
        )
    )

    positive_samples = (
        dataframe[
            dataframe["label"] == 1
        ]
    )

    negative_samples = (
        dataframe[
            dataframe["label"] == 0
        ]
    )

    neutral_positive_exists = (
        positive_samples[
            "has_sensitive_name"
        ]
        == 0
    ).any()

    sensitive_negative_exists = (
        negative_samples[
            "has_sensitive_name"
        ]
        == 1
    ).any()

    assert neutral_positive_exists
    assert sensitive_negative_exists


def test_dataset_can_be_saved_to_csv(
    tmp_path,
):
    output_path = (
        tmp_path
        / "dataset.csv"
    )

    dataframe = (
        save_synthetic_dataset(
            output_path=output_path,
            samples_per_class=10,
            seed=42,
        )
    )

    assert output_path.exists()

    loaded = pd.read_csv(
        output_path
    )

    assert len(loaded) == len(
        dataframe
    )


def test_invalid_sample_count_is_rejected():
    with pytest.raises(
        ValueError
    ):
        generate_synthetic_dataset(
            samples_per_class=0,
            seed=42,
        )