import pandas as pd
import pytest

from sklearn.pipeline import Pipeline

from leakguard.ml.baseline import (
    FEATURE_COLUMNS,
    build_baseline_pipeline,
    train_baseline,
    validate_training_dataframe,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)


def test_baseline_pipeline_is_created():
    model = build_baseline_pipeline()

    assert isinstance(
        model,
        Pipeline,
    )

    assert "scaler" in model.named_steps
    assert "classifier" in model.named_steps


def test_baseline_uses_expected_features():
    assert FEATURE_COLUMNS == [
        "length",
        "entropy",
        "digit_ratio",
        "uppercase_ratio",
        "special_ratio",
        "has_sensitive_name",
        "is_compact",
        "has_character_variety",
    ]


def test_baseline_training_returns_valid_metrics():
    dataframe = generate_synthetic_dataset_v2(
        samples_per_class=200,
        seed=42,
    )

    result = train_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    assert 0.0 <= result.accuracy <= 1.0
    assert 0.0 <= result.precision <= 1.0
    assert 0.0 <= result.recall <= 1.0
    assert 0.0 <= result.f1 <= 1.0
    assert 0.0 <= result.roc_auc <= 1.0


def test_baseline_split_size_is_correct():
    dataframe = generate_synthetic_dataset_v2(
        samples_per_class=100,
        seed=42,
    )

    result = train_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    assert result.train_samples == 160
    assert result.test_samples == 40


def test_confusion_matrix_counts_all_test_samples():
    dataframe = generate_synthetic_dataset_v2(
        samples_per_class=100,
        seed=42,
    )

    result = train_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    total_predictions = (
        result.true_negatives
        + result.false_positives
        + result.false_negatives
        + result.true_positives
    )

    assert total_predictions == result.test_samples


def test_missing_feature_is_rejected():
    dataframe = pd.DataFrame(
        {
            "label": [
                0,
                1,
            ],
        }
    )

    with pytest.raises(
        ValueError
    ):
        validate_training_dataframe(
            dataframe
        )
