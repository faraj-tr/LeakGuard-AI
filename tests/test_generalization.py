from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.generalization import (
    evaluate_numerical_generalization,
    evaluate_text_generalization,
)


def test_numerical_generalization_metrics_are_valid():
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

    result = (
        evaluate_numerical_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
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

    assert (
        0.0
        <= result.roc_auc
        <= 1.0
    )


def test_text_generalization_metrics_are_valid():
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

    result = (
        evaluate_text_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    assert (
        0.0
        <= result.accuracy
        <= 1.0
    )

    assert (
        0.0
        <= result.roc_auc
        <= 1.0
    )


def test_numerical_confusion_matrix_matches_challenge_size():
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

    result = (
        evaluate_numerical_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    total = (
        result.true_negatives
        + result.false_positives
        + result.false_negatives
        + result.true_positives
    )

    assert (
        total
        == len(challenge)
    )


def test_text_confusion_matrix_matches_challenge_size():
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

    result = (
        evaluate_text_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    total = (
        result.true_negatives
        + result.false_positives
        + result.false_negatives
        + result.true_positives
    )

    assert (
        total
        == len(challenge)
    )


def test_generalization_reports_dataset_sizes():
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

    result = (
        evaluate_numerical_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    assert (
        result.training_samples
        == 200
    )

    assert (
        result.challenge_samples
        == 100
    )