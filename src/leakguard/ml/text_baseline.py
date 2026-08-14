from dataclasses import dataclass

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
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


@dataclass
class TextBaselineResult:
    """
    Store the evaluation result of the
    LeakGuard TF-IDF text baseline.
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


def build_candidate_text(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """
    Combine variable names and values into
    one textual representation.

    Example:

        api_key = abc123
    """

    required_columns = {
        "variable_name",
        "value",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Dataset is missing text columns: "
            f"{sorted(missing_columns)}"
        )

    variable_names = (
        dataframe["variable_name"]
        .fillna("")
        .astype(str)
    )

    values = (
        dataframe["value"]
        .fillna("")
        .astype(str)
    )

    return (
        variable_names
        + " = "
        + values
    )


def validate_text_dataframe(
    dataframe: pd.DataFrame,
) -> None:
    """
    Validate columns and labels needed by
    the text baseline.
    """

    required_columns = {
        "variable_name",
        "value",
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
        dataframe["label"].unique()
    )

    if not labels.issubset(
        {0, 1}
    ):
        raise ValueError(
            "LeakGuard text baseline supports "
            "binary labels 0 and 1 only."
        )


def build_text_pipeline() -> Pipeline:
    """
    Build the LeakGuard TF-IDF character
    n-gram Logistic Regression baseline.
    """

    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=(3, 5),
                    min_df=2,
                    sublinear_tf=True,
                    lowercase=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1500,
                    random_state=42,
                ),
            ),
        ]
    )


def train_text_baseline(
    dataframe: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> TextBaselineResult:
    """
    Train and evaluate the LeakGuard
    TF-IDF text baseline.

    Labels:
        0 = non-secret
        1 = secret
    """

    validate_text_dataframe(
        dataframe
    )

    if not 0.0 < test_size < 1.0:
        raise ValueError(
            "test_size must be between "
            "0 and 1."
        )

    X = build_candidate_text(
        dataframe
    )

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

    model = build_text_pipeline()

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

    return TextBaselineResult(
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