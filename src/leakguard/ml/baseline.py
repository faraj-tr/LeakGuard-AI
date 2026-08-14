from dataclasses import dataclass

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "length",
    "entropy",
    "digit_ratio",
    "uppercase_ratio",
    "special_ratio",
    "has_sensitive_name",
    "is_compact",
    "has_character_variety",
]


@dataclass
class BaselineResult:
    """
    Store the evaluation result of the
    LeakGuard numerical baseline model.
    """

    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int

    train_samples: int
    test_samples: int

    model: Pipeline


def validate_training_dataframe(
    dataframe: pd.DataFrame,
) -> None:
    """
    Ensure that the dataset contains all
    columns required by the baseline model.
    """

    required_columns = {
        *FEATURE_COLUMNS,
        "label",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:

        raise ValueError(
            "Dataset is missing required "
            f"columns: {sorted(missing_columns)}"
        )

    labels = set(
        dataframe[
            "label"
        ].unique()
    )

    if not labels.issubset(
        {0, 1}
    ):
        raise ValueError(
            "LeakGuard baseline supports "
            "binary labels 0 and 1 only."
        )


def build_baseline_pipeline() -> Pipeline:
    """
    Build the numerical Logistic Regression
    baseline.

    StandardScaler and LogisticRegression
    are intentionally kept inside one
    sklearn Pipeline.
    """

    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


def train_baseline(
    dataframe: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> BaselineResult:
    """
    Train and evaluate the first LeakGuard
    numerical machine-learning baseline.

    Labels:
        0 = non-secret
        1 = secret
    """

    validate_training_dataframe(
        dataframe
    )

    if not 0.0 < test_size < 1.0:
        raise ValueError(
            "test_size must be between "
            "0 and 1."
        )

    X = dataframe[
        FEATURE_COLUMNS
    ].copy()

    y = dataframe[
        "label"
    ].copy()

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    model = (
        build_baseline_pipeline()
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    probabilities = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    )

    (
        true_negatives,
        false_positives,
        false_negatives,
        true_positives,
    ) = matrix.ravel()

    return BaselineResult(
        accuracy=float(
            accuracy_score(
                y_test,
                predictions,
            )
        ),

        precision=float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),

        recall=float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),

        f1=float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),

        roc_auc=float(
            roc_auc_score(
                y_test,
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

        train_samples=len(
            X_train
        ),

        test_samples=len(
            X_test
        ),

        model=model,
    )