import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)
from sklearn.preprocessing import (
    FunctionTransformer,
    StandardScaler,
)
from sklearn.linear_model import (
    LogisticRegression,
)
from sklearn.pipeline import Pipeline

from leakguard.ml.baseline import (
    FEATURE_COLUMNS,
    validate_training_dataframe,
)
from leakguard.ml.generalization import (
    GeneralizationResult,
    calculate_metrics,
)
from leakguard.ml.text_baseline import (
    build_candidate_text,
    validate_text_dataframe,
)


TEXT_COLUMN = "candidate_text"


def flatten_text_column(
    values,
):
    """
    Convert the single text column produced
    by ColumnTransformer into a 1D sequence
    accepted by TfidfVectorizer.
    """

    if isinstance(
        values,
        pd.DataFrame,
    ):
        return (
            values.iloc[:, 0]
            .fillna("")
            .astype(str)
        )

    array = np.asarray(
        values
    )

    return (
        array
        .reshape(-1)
        .astype(str)
    )


def prepare_hybrid_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare one dataframe for the hybrid
    text + numerical model.
    """

    validate_training_dataframe(
        dataframe
    )

    validate_text_dataframe(
        dataframe
    )

    prepared = dataframe.copy()

    prepared[
        TEXT_COLUMN
    ] = build_candidate_text(
        dataframe
    )

    return prepared


def build_hybrid_pipeline() -> Pipeline:
    """
    Build the LeakGuard Hybrid Model v1.

    Text branch:
        Character TF-IDF.

    Numerical branch:
        Standardized LeakGuard features.

    Both branches are combined before
    Logistic Regression classification.
    """

    text_pipeline = Pipeline(
        steps=[
            (
                "flatten",
                FunctionTransformer(
                    flatten_text_column,
                    validate=False,
                ),
            ),
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
        ]
    )

    numerical_pipeline = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    feature_processor = (
        ColumnTransformer(
            transformers=[
                (
                    "text",
                    text_pipeline,
                    [TEXT_COLUMN],
                ),
                (
                    "numerical",
                    numerical_pipeline,
                    FEATURE_COLUMNS,
                ),
            ],
            sparse_threshold=1.0,
        )
    )

    return Pipeline(
        steps=[
            (
                "features",
                feature_processor,
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate_hybrid_generalization(
    training_dataframe: pd.DataFrame,
    challenge_dataframe: pd.DataFrame,
) -> GeneralizationResult:
    """
    Train Hybrid Model v1 only on
    Synthetic Dataset v2.

    Evaluate exclusively on the independent
    Challenge Dataset v1.
    """

    training = (
        prepare_hybrid_dataframe(
            training_dataframe
        )
    )

    challenge = (
        prepare_hybrid_dataframe(
            challenge_dataframe
        )
    )

    model = (
        build_hybrid_pipeline()
    )

    model.fit(
        training,
        training["label"],
    )

    predictions = model.predict(
        challenge
    )

    probabilities = (
        model.predict_proba(
            challenge
        )[:, 1]
    )

    return calculate_metrics(
        model_name=(
            "Hybrid TF-IDF + "
            "Numerical Logistic Regression"
        ),
        y_true=challenge[
            "label"
        ],
        predictions=predictions,
        probabilities=probabilities,
        training_samples=len(
            training
        ),
        challenge_samples=len(
            challenge
        ),
    )