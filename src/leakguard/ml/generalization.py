from dataclasses import dataclass

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from leakguard.ml.baseline import (
    FEATURE_COLUMNS,
    build_baseline_pipeline,
    validate_training_dataframe,
)
from leakguard.ml.text_baseline import (
    build_candidate_text,
    build_text_pipeline,
    validate_text_dataframe,
)


@dataclass
class GeneralizationResult:
    """
    Store evaluation results for a model
    tested on an independent challenge set.
    """

    model_name: str

    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int

    training_samples: int
    challenge_samples: int


def calculate_metrics(
    model_name: str,
    y_true,
    predictions,
    probabilities,
    training_samples: int,
    challenge_samples: int,
) -> GeneralizationResult:
    """
    Calculate classification metrics for
    an independent challenge dataset.
    """

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    (
        true_negatives,
        false_positives,
        false_negatives,
        true_positives,
    ) = matrix.ravel()

    return GeneralizationResult(
        model_name=model_name,

        accuracy=float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),

        precision=float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        recall=float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        f1=float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        roc_auc=float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),

        true_negatives=int(
            true_negatives
        ),

        false_positives=int(
            false_positives
        ),

        false_negatives=int(
            false_negatives
        ),

        true_positives=int(
            true_positives
        ),

        training_samples=(
            training_samples
        ),

        challenge_samples=(
            challenge_samples
        ),
    )


def evaluate_numerical_generalization(
    training_dataframe: pd.DataFrame,
    challenge_dataframe: pd.DataFrame,
) -> GeneralizationResult:
    """
    Train the numerical baseline using only
    Synthetic Dataset v2 and evaluate it on
    the independent Challenge Dataset v1.
    """

    validate_training_dataframe(
        training_dataframe
    )

    validate_training_dataframe(
        challenge_dataframe
    )

    X_train = training_dataframe[
        FEATURE_COLUMNS
    ].copy()

    y_train = training_dataframe[
        "label"
    ].copy()

    X_challenge = challenge_dataframe[
        FEATURE_COLUMNS
    ].copy()

    y_challenge = challenge_dataframe[
        "label"
    ].copy()

    model = build_baseline_pipeline()

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_challenge
    )

    probabilities = (
        model.predict_proba(
            X_challenge
        )[:, 1]
    )

    return calculate_metrics(
        model_name=(
            "Numerical Logistic Regression"
        ),
        y_true=y_challenge,
        predictions=predictions,
        probabilities=probabilities,
        training_samples=len(
            training_dataframe
        ),
        challenge_samples=len(
            challenge_dataframe
        ),
    )


def evaluate_text_generalization(
    training_dataframe: pd.DataFrame,
    challenge_dataframe: pd.DataFrame,
) -> GeneralizationResult:
    """
    Train the TF-IDF baseline using only
    Synthetic Dataset v2 and evaluate it on
    Challenge Dataset v1.
    """

    validate_text_dataframe(
        training_dataframe
    )

    validate_text_dataframe(
        challenge_dataframe
    )

    X_train = build_candidate_text(
        training_dataframe
    )

    y_train = training_dataframe[
        "label"
    ].copy()

    X_challenge = build_candidate_text(
        challenge_dataframe
    )

    y_challenge = challenge_dataframe[
        "label"
    ].copy()

    model = build_text_pipeline()

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_challenge
    )

    probabilities = (
        model.predict_proba(
            X_challenge
        )[:, 1]
    )

    return calculate_metrics(
        model_name=(
            "Character TF-IDF "
            "Logistic Regression"
        ),
        y_true=y_challenge,
        predictions=predictions,
        probabilities=probabilities,
        training_samples=len(
            training_dataframe
        ),
        challenge_samples=len(
            challenge_dataframe
        ),
    )