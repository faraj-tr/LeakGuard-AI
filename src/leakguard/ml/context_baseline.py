import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from leakguard.ml.baseline import (
    FEATURE_COLUMNS,
)
from leakguard.ml.context_features import (
    extract_context_features,
)
from leakguard.ml.generalization import (
    GeneralizationResult,
    calculate_metrics,
)
from leakguard.ml.text_baseline import (
    validate_text_dataframe,
)


CONTEXT_ONLY_COLUMNS = [
    "looks_like_uuid",
    "looks_like_fixed_hash",
    "is_hex_only",
    "looks_like_reference",
    "looks_like_placeholder",
    "has_public_frontend_prefix",
    "has_identifier_name",
    "looks_like_jwt",
    "looks_like_passphrase",
]


CONTEXT_FEATURE_COLUMNS = (
    FEATURE_COLUMNS
    + CONTEXT_ONLY_COLUMNS
)


def build_context_feature_frame(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Recompute Candidate v2 features directly
    from variable_name and value.

    sample_type, framework, source, and
    other dataset metadata are never used
    as model features.
    """

    validate_text_dataframe(
        dataframe
    )

    records = []

    for row in dataframe[
        [
            "variable_name",
            "value",
        ]
    ].itertuples(
        index=False
    ):
        features = extract_context_features(
            variable_name=str(
                row.variable_name
            ),
            value=str(
                row.value
            ),
        )

        records.append(
            features
        )

    feature_frame = pd.DataFrame(
        records
    )

    return feature_frame[
        CONTEXT_FEATURE_COLUMNS
    ].copy()


def build_context_pipeline() -> Pipeline:
    """
    Build Candidate v2 contextual numerical
    Logistic Regression baseline.
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
                    max_iter=1500,
                    random_state=42,
                ),
            ),
        ]
    )


def fit_context_model(
    training_dataframe: pd.DataFrame,
) -> Pipeline:
    """
    Fit Candidate v2 contextual model.
    """

    X_train = build_context_feature_frame(
        training_dataframe
    )

    y_train = training_dataframe[
        "label"
    ].copy()

    model = build_context_pipeline()

    model.fit(
        X_train,
        y_train,
    )

    return model


def evaluate_context_generalization(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> GeneralizationResult:
    """
    Train on Synthetic Dataset v2 and
    evaluate on Challenge Dataset v1.

    Challenge v1 is development data only.
    """

    X_train = build_context_feature_frame(
        training_dataframe
    )

    y_train = training_dataframe[
        "label"
    ].copy()

    X_development = (
        build_context_feature_frame(
            development_dataframe
        )
    )

    y_development = development_dataframe[
        "label"
    ].copy()

    model = build_context_pipeline()

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_development
    )

    probabilities = model.predict_proba(
        X_development
    )[:, 1]

    return calculate_metrics(
        model_name=(
            "Candidate v2 Contextual "
            "Logistic Regression"
        ),
        y_true=y_development,
        predictions=predictions,
        probabilities=probabilities,
        training_samples=len(
            training_dataframe
        ),
        challenge_samples=len(
            development_dataframe
        ),
    )


def get_context_coefficients(
    model: Pipeline,
) -> pd.DataFrame:
    """
    Return Logistic Regression feature
    coefficients for development analysis.
    """

    classifier = model.named_steps[
        "classifier"
    ]

    coefficients = (
        classifier.coef_[0]
    )

    result = pd.DataFrame(
        {
            "feature": (
                CONTEXT_FEATURE_COLUMNS
            ),
            "coefficient": coefficients,
        }
    )

    result[
        "absolute_coefficient"
    ] = result[
        "coefficient"
    ].abs()

    return (
        result
        .sort_values(
            "absolute_coefficient",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )
