import pytest

from leakguard.ml.candidate_v2_devset import (
    generate_candidate_v2_devset,
)
from leakguard.ml.candidate_v2_fusion import (
    DEFAULT_TEXT_WEIGHTS,
    DEFAULT_THRESHOLDS,
    build_candidate_v2_probability_frame,
    build_fusion_decisions,
    evaluate_candidate_v2_fusion,
    search_candidate_v2_fusion,
    validate_fusion_parameters,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


def create_data():
    training = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    development = (
        generate_candidate_v2_devset(
            samples_per_class=90,
            seed=260815,
        )
    )

    return training, development


def test_probability_frame_matches_development_size():
    training, development = (
        create_data()
    )

    results = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert len(results) == len(
        development
    )

    assert (
        "context_probability"
        in results.columns
    )

    assert (
        "text_probability"
        in results.columns
    )


def test_fusion_decisions_have_expected_columns():
    training, development = (
        create_data()
    )

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    decisions = (
        build_fusion_decisions(
            probability_frame=probabilities,
            text_weight=0.7,
            threshold=0.5,
        )
    )

    assert (
        "fusion_probability"
        in decisions.columns
    )

    assert (
        "fusion_prediction"
        in decisions.columns
    )


def test_fusion_probabilities_are_valid():
    training, development = (
        create_data()
    )

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    decisions = (
        build_fusion_decisions(
            probability_frame=probabilities,
            text_weight=0.7,
            threshold=0.5,
        )
    )

    assert (
        (
            decisions[
                "fusion_probability"
            ]
            >= 0.0
        )
        & (
            decisions[
                "fusion_probability"
            ]
            <= 1.0
        )
    ).all()


def test_fusion_metrics_are_valid():
    training, development = (
        create_data()
    )

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    result = (
        evaluate_candidate_v2_fusion(
            probability_frame=probabilities,
            text_weight=0.7,
            threshold=0.5,
            training_samples=len(
                training
            ),
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


def test_fusion_search_has_expected_number_of_rows():
    training, development = (
        create_data()
    )

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    results = (
        search_candidate_v2_fusion(
            probability_frame=probabilities,
            training_samples=len(
                training
            ),
        )
    )

    expected = (
        len(DEFAULT_TEXT_WEIGHTS)
        * len(DEFAULT_THRESHOLDS)
    )

    assert len(results) == expected


def test_fusion_search_is_sorted_by_f1():
    training, development = (
        create_data()
    )

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    results = (
        search_candidate_v2_fusion(
            probability_frame=probabilities,
            training_samples=len(
                training
            ),
        )
    )

    values = results[
        "f1"
    ].tolist()

    assert values == sorted(
        values,
        reverse=True,
    )


def test_invalid_fusion_parameters_are_rejected():
    with pytest.raises(
        ValueError
    ):
        validate_fusion_parameters(
            text_weight=1.5,
            threshold=0.5,
        )

    with pytest.raises(
        ValueError
    ):
        validate_fusion_parameters(
            text_weight=0.7,
            threshold=-0.1,
        )
