from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.locked_fusion import (
    LOCKED_NUMERICAL_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
    evaluate_locked_fusion,
    get_locked_configuration,
)


def test_locked_weights_sum_to_one():
    assert (
        LOCKED_TEXT_WEIGHT
        + LOCKED_NUMERICAL_WEIGHT
    ) == 1.0


def test_locked_configuration_values():
    configuration = (
        get_locked_configuration()
    )

    assert (
        configuration[
            "text_weight"
        ]
        == 0.60
    )

    assert (
        configuration[
            "numerical_weight"
        ]
        == 0.40
    )

    assert (
        configuration[
            "threshold"
        ]
        == 0.40
    )


def test_locked_fusion_metrics_are_valid():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    evaluation = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    result = (
        evaluate_locked_fusion(
            training_dataframe=training,
            evaluation_dataframe=evaluation,
        )
    )

    assert (
        0.0
        <= result.accuracy
        <= 1.0
    )

    assert (
        0.0
        <= result.precision
        <= 1.0
    )

    assert (
        0.0
        <= result.recall
        <= 1.0
    )

    assert (
        0.0
        <= result.f1
        <= 1.0
    )


def test_locked_fusion_counts_all_samples():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    evaluation = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    result = (
        evaluate_locked_fusion(
            training_dataframe=training,
            evaluation_dataframe=evaluation,
        )
    )

    total = (
        result.true_positives
        + result.true_negatives
        + result.false_positives
        + result.false_negatives
    )

    assert total == len(
        evaluation
    )