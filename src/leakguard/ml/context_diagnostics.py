import pandas as pd

from leakguard.ml.context_baseline import (
    CONTEXT_ONLY_COLUMNS,
    build_context_feature_frame,
    build_context_pipeline,
)


def build_context_predictions(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Train the contextual Candidate v2 model
    and return development predictions.

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

    model = build_context_pipeline()

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_development
    )

    probabilities = (
        model.predict_proba(
            X_development
        )[:, 1]
    )

    results = (
        development_dataframe
        .copy()
        .reset_index(
            drop=True
        )
    )

    results[
        "context_prediction"
    ] = predictions

    results[
        "context_probability"
    ] = probabilities

    return results


def get_context_false_negatives(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return secrets missed by the contextual
    development model.
    """

    return results[
        (
            results["label"] == 1
        )
        & (
            results[
                "context_prediction"
            ] == 0
        )
    ].copy()


def get_context_false_positives(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return safe values incorrectly classified
    as secrets.
    """

    return results[
        (
            results["label"] == 0
        )
        & (
            results[
                "context_prediction"
            ] == 1
        )
    ].copy()


def get_error_type_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Group development errors by sample_type.

    sample_type is used only for diagnostics,
    never as a model feature.
    """

    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "sample_type",
                "count",
            ]
        )

    return (
        dataframe[
            "sample_type"
        ]
        .value_counts()
        .rename_axis(
            "sample_type"
        )
        .reset_index(
            name="count"
        )
    )


def get_feature_activation_report(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Report how often each Candidate v2
    contextual feature activates.

    This helps identify features that exist
    in code but have no training support.
    """

    features = build_context_feature_frame(
        dataframe
    )

    records = []

    for feature in CONTEXT_ONLY_COLUMNS:

        activated = int(
            (
                features[feature]
                == 1
            ).sum()
        )

        records.append(
            {
                "dataset": dataset_name,
                "feature": feature,
                "activated": activated,
                "total": len(
                    features
                ),
                "activation_rate": (
                    activated
                    / len(features)
                    if len(features)
                    else 0.0
                ),
            }
        )

    return pd.DataFrame(
        records
    )


def compare_feature_activation(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare contextual feature support
    between training and development data.
    """

    training_report = (
        get_feature_activation_report(
            training_dataframe,
            "training_v2",
        )
    )

    development_report = (
        get_feature_activation_report(
            development_dataframe,
            "challenge_v1_dev",
        )
    )

    return pd.concat(
        [
            training_report,
            development_report,
        ],
        ignore_index=True,
    )
