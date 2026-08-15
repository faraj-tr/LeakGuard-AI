from sklearn.pipeline import Pipeline

from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.context_baseline import (
    CONTEXT_FEATURE_COLUMNS,
    build_context_feature_frame,
    build_context_pipeline,
    evaluate_context_generalization,
    fit_context_model,
    get_context_coefficients,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)


def test_context_feature_frame_has_expected_columns():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=20,
            seed=42,
        )
    )

    features = (
        build_context_feature_frame(
            dataframe
        )
    )

    assert list(
        features.columns
    ) == CONTEXT_FEATURE_COLUMNS


def test_context_feature_frame_matches_dataset_size():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=20,
            seed=42,
        )
    )

    features = (
        build_context_feature_frame(
            dataframe
        )
    )

    assert len(features) == len(
        dataframe
    )


def test_context_pipeline_is_created():
    model = build_context_pipeline()

    assert isinstance(
        model,
        Pipeline,
    )

    assert (
        "scaler"
        in model.named_steps
    )

    assert (
        "classifier"
        in model.named_steps
    )


def test_context_model_can_be_fitted():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    model = fit_context_model(
        training
    )

    assert hasattr(
        model,
        "predict"
    )

    assert hasattr(
        model,
        "predict_proba"
    )


def test_context_generalization_metrics_are_valid():
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

    result = (
        evaluate_context_generalization(
            training_dataframe=training,
            development_dataframe=development,
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


def test_context_coefficients_match_features():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    model = fit_context_model(
        training
    )

    coefficients = (
        get_context_coefficients(
            model
        )
    )

    assert len(
        coefficients
    ) == len(
        CONTEXT_FEATURE_COLUMNS
    )

    assert set(
        coefficients["feature"]
    ) == set(
        CONTEXT_FEATURE_COLUMNS
    )
