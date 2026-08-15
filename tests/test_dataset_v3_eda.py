from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)
from leakguard.ml.dataset_v3_eda import (
    get_context_activation_by_label,
    get_context_overlap_summary,
    get_context_secret_rates,
    get_sensitive_name_analysis,
    summarize_dataset_v3,
    validate_dataset_v3,
)


def create_dataset():
    return (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )


def test_v3_eda_summary_is_balanced():
    dataframe = create_dataset()

    summary = summarize_dataset_v3(
        dataframe
    )

    assert (
        summary[
            "secret_samples"
        ]
        == 140
    )

    assert (
        summary[
            "safe_samples"
        ]
        == 140
    )


def test_v3_validation_has_valid_labels():
    dataframe = create_dataset()

    validation = validate_dataset_v3(
        dataframe
    )

    assert (
        validation[
            "valid_labels"
        ]
        is True
    )

    assert (
        validation[
            "duplicate_sample_ids"
        ]
        == 0
    )


def test_context_overlap_contains_both_class_features():
    dataframe = create_dataset()

    overlap = (
        get_context_overlap_summary(
            dataframe
        )
    )

    assert (
        overlap[
            "appears_in_both_classes"
        ]
    ).all()


def test_context_secret_rates_are_valid():
    dataframe = create_dataset()

    report = (
        get_context_secret_rates(
            dataframe
        )
    )

    assert (
        (
            report[
                "secret_rate_when_active"
            ]
            >= 0.0
        )
        & (
            report[
                "secret_rate_when_active"
            ]
            <= 1.0
        )
    ).all()


def test_context_activation_has_both_labels():
    dataframe = create_dataset()

    report = (
        get_context_activation_by_label(
            dataframe
        )
    )

    assert set(
        report["label"]
    ) == {
        0,
        1,
    }


def test_sensitive_name_analysis_counts_all_samples():
    dataframe = create_dataset()

    report = (
        get_sensitive_name_analysis(
            dataframe
        )
    )

    assert (
        report[
            "samples"
        ].sum()
        == len(dataframe)
    )
