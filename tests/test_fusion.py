import numpy as np
import pytest

from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.challenge_analysis import (
    build_challenge_predictions,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.fusion import (
    calculate_fusion_probability,
    evaluate_fusion_configuration,
    rank_security_configurations,
    search_fusion_configurations,
)


def create_predictions():
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

    return build_challenge_predictions(
        training_dataframe=training,
        challenge_dataframe=development,
    )


def test_equal_weight_fusion():
    numerical = np.array(
        [0.2, 0.8]
    )

    text = np.array(
        [0.6, 0.4]
    )

    result = (
        calculate_fusion_probability(
            numerical_probability=(
                numerical
            ),
            text_probability=text,
            text_weight=0.5,
        )
    )

    assert np.allclose(
        result,
        [0.4, 0.6],
    )


def test_invalid_text_weight_is_rejected():
    with pytest.raises(
        ValueError
    ):
        calculate_fusion_probability(
            numerical_probability=[
                0.5
            ],
            text_probability=[
                0.5
            ],
            text_weight=1.5,
        )


def test_fusion_metrics_are_valid():
    results = create_predictions()

    evaluation = (
        evaluate_fusion_configuration(
            results=results,
            text_weight=0.7,
            threshold=0.45,
        )
    )

    assert (
        0.0
        <= evaluation.accuracy
        <= 1.0
    )

    assert (
        0.0
        <= evaluation.precision
        <= 1.0
    )

    assert (
        0.0
        <= evaluation.recall
        <= 1.0
    )

    assert (
        0.0
        <= evaluation.f1
        <= 1.0
    )


def test_fusion_counts_all_samples():
    results = create_predictions()

    evaluation = (
        evaluate_fusion_configuration(
            results=results,
            text_weight=0.7,
            threshold=0.45,
        )
    )

    total = (
        evaluation.true_positives
        + evaluation.true_negatives
        + evaluation.false_positives
        + evaluation.false_negatives
    )

    assert total == len(results)


def test_search_returns_multiple_configurations():
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

    results = (
        search_fusion_configurations(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert len(results) > 1

    assert {
        "text_weight",
        "threshold",
        "recall",
        "f1",
        "false_negatives",
    }.issubset(
        results.columns
    )


def test_security_ranking_respects_recall():
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

    results = (
        search_fusion_configurations(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    ranked = (
        rank_security_configurations(
            results,
            minimum_recall=0.80,
        )
    )

    if (
        results["recall"]
        >= 0.80
    ).any():

        assert (
            ranked["recall"]
            >= 0.80
        ).all()