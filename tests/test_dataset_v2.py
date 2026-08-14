import pandas as pd
import pytest

from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
    save_synthetic_dataset_v2,
)


def test_v2_dataset_is_balanced():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
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

    assert len(dataframe) == 200
    assert counts[0] == 100
    assert counts[1] == 100


def test_v2_reduces_variable_name_bias():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    positives = dataframe[
        dataframe["label"] == 1
    ]

    negatives = dataframe[
        dataframe["label"] == 0
    ]

    positive_sensitive = int(
        (
            positives[
                "has_sensitive_name"
            ]
            == 1
        ).sum()
    )

    negative_sensitive = int(
        (
            negatives[
                "has_sensitive_name"
            ]
            == 1
        ).sum()
    )

    assert positive_sensitive == 50
    assert negative_sensitive == 40


def test_v2_contains_secret_with_neutral_name():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    result = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "has_sensitive_name"
            ]
            == 0
        )
    ]

    assert len(result) == 50


def test_v2_contains_safe_sensitive_names():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    result = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "has_sensitive_name"
            ]
            == 1
        )
    ]

    assert len(result) == 40


def test_v2_has_feature_overlap_between_classes():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=200,
            seed=42,
        )
    )

    positives = dataframe[
        dataframe["label"] == 1
    ]

    negatives = dataframe[
        dataframe["label"] == 0
    ]

    positive_non_compact_exists = (
        positives[
            "is_compact"
        ]
        == 0
    ).any()

    high_entropy_negative_exists = (
        negatives[
            "entropy"
        ]
        >= 3.5
    ).any()

    assert positive_non_compact_exists
    assert high_entropy_negative_exists


def test_v2_generation_is_reproducible():
    first = (
        generate_synthetic_dataset_v2(
            samples_per_class=50,
            seed=123,
        )
    )

    second = (
        generate_synthetic_dataset_v2(
            samples_per_class=50,
            seed=123,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_v2_can_be_saved_to_csv(
    tmp_path,
):
    output_path = (
        tmp_path
        / "dataset_v2.csv"
    )

    dataframe = (
        save_synthetic_dataset_v2(
            output_path=output_path,
            samples_per_class=50,
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


def test_v2_rejects_invalid_sample_count():
    with pytest.raises(
        ValueError
    ):
        generate_synthetic_dataset_v2(
            samples_per_class=0,
            seed=42,
        )