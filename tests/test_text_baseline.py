import pandas as pd
import pytest

from sklearn.pipeline import Pipeline

from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.text_baseline import (
    build_candidate_text,
    build_text_pipeline,
    train_text_baseline,
    validate_text_dataframe,
)


def test_candidate_text_combines_name_and_value():
    dataframe = pd.DataFrame(
        {
            "variable_name": [
                "api_key",
            ],
            "value": [
                "example-value",
            ],
        }
    )

    text = build_candidate_text(
        dataframe
    )

    assert (
        text.iloc[0]
        == "api_key = example-value"
    )


def test_text_pipeline_is_created():
    model = build_text_pipeline()

    assert isinstance(
        model,
        Pipeline,
    )

    assert "tfidf" in (
        model.named_steps
    )

    assert "classifier" in (
        model.named_steps
    )


def test_text_baseline_returns_valid_metrics():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=200,
            seed=42,
        )
    )

    result = train_text_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
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


def test_text_baseline_split_size():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    result = train_text_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    assert (
        result.train_samples
        == 160
    )

    assert (
        result.test_samples
        == 40
    )


def test_text_confusion_matrix_counts_test_set():
    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    result = train_text_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    total = (
        result.true_negatives
        + result.false_positives
        + result.false_negatives
        + result.true_positives
    )

    assert (
        total
        == result.test_samples
    )


def test_text_dataframe_rejects_missing_columns():
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
        validate_text_dataframe(
            dataframe
        )