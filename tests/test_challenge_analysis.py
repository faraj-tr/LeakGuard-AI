from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.challenge_analysis import (
    build_challenge_predictions,
    get_agreement_summary,
    get_model_errors,
    get_type_distribution,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)


def create_test_results():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    challenge = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    return build_challenge_predictions(
        training_dataframe=training,
        challenge_dataframe=challenge,
    )


def test_challenge_predictions_match_dataset_size():
    results = create_test_results()

    assert len(results) == 100


def test_challenge_prediction_columns_exist():
    results = create_test_results()

    required_columns = {
        "numerical_prediction",
        "numerical_probability",
        "text_prediction",
        "text_probability",
        "numerical_correct",
        "text_correct",
    }

    assert required_columns.issubset(
        set(
            results.columns
        )
    )


def test_probabilities_are_valid():
    results = create_test_results()

    assert (
        (
            results[
                "numerical_probability"
            ]
            >= 0.0
        )
        & (
            results[
                "numerical_probability"
            ]
            <= 1.0
        )
    ).all()

    assert (
        (
            results[
                "text_probability"
            ]
            >= 0.0
        )
        & (
            results[
                "text_probability"
            ]
            <= 1.0
        )
    ).all()


def test_agreement_counts_all_samples():
    results = create_test_results()

    summary = (
        get_agreement_summary(
            results
        )
    )

    total = (
        summary["both_correct"]
        + summary["both_wrong"]
        + summary[
            "numerical_only_correct"
        ]
        + summary[
            "text_only_correct"
        ]
    )

    assert total == len(results)


def test_error_distribution_matches_error_count():
    results = create_test_results()

    errors = get_model_errors(
        results=results,
        prediction_column=(
            "text_prediction"
        ),
        error_type="false_positive",
    )

    distribution = (
        get_type_distribution(
            errors
        )
    )

    assert (
        distribution[
            "count"
        ].sum()
        == len(errors)
    )