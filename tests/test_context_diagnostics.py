from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.context_diagnostics import (
    build_context_predictions,
    compare_feature_activation,
    get_context_false_negatives,
    get_context_false_positives,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)


def create_data():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    development = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    return training, development


def test_context_predictions_match_development_size():
    training, development = (
        create_data()
    )

    results = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert len(results) == len(
        development
    )


def test_context_prediction_columns_exist():
    training, development = (
        create_data()
    )

    results = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        "context_prediction"
        in results.columns
    )

    assert (
        "context_probability"
        in results.columns
    )


def test_context_errors_are_valid_subsets():
    training, development = (
        create_data()
    )

    results = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    false_negatives = (
        get_context_false_negatives(
            results
        )
    )

    false_positives = (
        get_context_false_positives(
            results
        )
    )

    assert (
        false_negatives[
            "label"
        ]
        == 1
    ).all()

    assert (
        false_positives[
            "label"
        ]
        == 0
    ).all()


def test_feature_activation_report_contains_both_sets():
    training, development = (
        create_data()
    )

    report = (
        compare_feature_activation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert set(
        report["dataset"]
    ) == {
        "training_v2",
        "challenge_v1_dev",
    }


def test_activation_rates_are_valid():
    training, development = (
        create_data()
    )

    report = (
        compare_feature_activation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        (
            report[
                "activation_rate"
            ]
            >= 0.0
        )
        & (
            report[
                "activation_rate"
            ]
            <= 1.0
        )
    ).all()
