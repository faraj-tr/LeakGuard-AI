from sklearn.pipeline import Pipeline

from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.hybrid import (
    TEXT_COLUMN,
    build_hybrid_pipeline,
    evaluate_hybrid_generalization,
    prepare_hybrid_dataframe,
)


def test_prepare_hybrid_dataframe_adds_text():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=20,
            seed=42,
        )
    )

    prepared = (
        prepare_hybrid_dataframe(
            dataframe
        )
    )

    assert (
        TEXT_COLUMN
        in prepared.columns
    )

    assert len(
        prepared
    ) == len(
        dataframe
    )


def test_hybrid_candidate_text_contains_name():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=10,
            seed=42,
        )
    )

    prepared = (
        prepare_hybrid_dataframe(
            dataframe
        )
    )

    first_name = str(
        prepared.iloc[0][
            "variable_name"
        ]
    )

    first_text = str(
        prepared.iloc[0][
            TEXT_COLUMN
        ]
    )

    assert (
        first_name
        in first_text
    )


def test_hybrid_pipeline_is_created():
    model = (
        build_hybrid_pipeline()
    )

    assert isinstance(
        model,
        Pipeline,
    )

    assert (
        "features"
        in model.named_steps
    )

    assert (
        "classifier"
        in model.named_steps
    )


def test_hybrid_generalization_metrics_are_valid():
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
        evaluate_hybrid_generalization(
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


def test_hybrid_confusion_matrix_matches_challenge():
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
        evaluate_hybrid_generalization(
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