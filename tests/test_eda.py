import pandas as pd

from leakguard.ml.dataset import (
    generate_synthetic_dataset,
)
from leakguard.ml.eda import (
    get_feature_summary,
    get_hard_example_counts,
    get_sample_type_distribution,
    get_sensitive_name_analysis,
    summarize_dataset,
    validate_dataset,
)


def test_dataset_validation_passes():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=20,
            seed=42,
        )
    )

    validation = (
        validate_dataset(
            dataframe
        )
    )

    assert validation[
        "missing_columns"
    ] == []

    assert validation[
        "valid_labels"
    ] is True

    assert validation[
        "missing_values"
    ] == 0

    assert validation[
        "duplicate_sample_ids"
    ] == 0


def test_dataset_summary_is_balanced():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=20,
            seed=42,
        )
    )

    summary = (
        summarize_dataset(
            dataframe
        )
    )

    assert summary[
        "total_samples"
    ] == 40

    assert summary[
        "secret_samples"
    ] == 20

    assert summary[
        "non_secret_samples"
    ] == 20

    assert summary[
        "secret_ratio"
    ] == 0.5


def test_feature_summary_contains_both_labels():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=20,
            seed=42,
        )
    )

    summary = (
        get_feature_summary(
            dataframe
        )
    )

    assert 0 in summary.index
    assert 1 in summary.index

    assert "entropy" in (
        summary.columns
    )


def test_dataset_contains_positive_hard_examples():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=50,
            seed=42,
        )
    )

    counts = (
        get_hard_example_counts(
            dataframe
        )
    )

    assert (
        counts[
            "positive_without_sensitive_name"
        ]
        > 0
    )


def test_dataset_contains_negative_hard_examples():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=50,
            seed=42,
        )
    )

    counts = (
        get_hard_example_counts(
            dataframe
        )
    )

    assert (
        counts[
            "negative_with_sensitive_name"
        ]
        > 0
    )


def test_sensitive_name_analysis():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=50,
            seed=42,
        )
    )

    analysis = (
        get_sensitive_name_analysis(
            dataframe
        )
    )

    assert (
        analysis[
            "sensitive_name_samples"
        ]
        > 0
    )

    assert (
        analysis[
            "non_sensitive_name_samples"
        ]
        > 0
    )

    assert (
        0.0
        <= analysis[
            "sensitive_name_secret_rate"
        ]
        <= 1.0
    )


def test_sample_type_distribution_has_counts():
    dataframe = (
        generate_synthetic_dataset(
            samples_per_class=50,
            seed=42,
        )
    )

    distribution = (
        get_sample_type_distribution(
            dataframe
        )
    )

    assert isinstance(
        distribution,
        pd.DataFrame,
    )

    assert "count" in (
        distribution.columns
    )

    assert distribution[
        "count"
    ].sum() == 100