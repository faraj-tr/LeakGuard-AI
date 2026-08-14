import pandas as pd

from sklearn.model_selection import train_test_split

from leakguard.ml.baseline import (
    FEATURE_COLUMNS,
    build_baseline_pipeline,
    validate_training_dataframe,
)


def analyze_baseline_errors(
    dataframe: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> dict:
    """
    Train the LeakGuard baseline and return
    detailed information about misclassified
    test samples.
    """

    validate_training_dataframe(
        dataframe
    )

    X = dataframe[
        FEATURE_COLUMNS
    ].copy()

    y = dataframe[
        "label"
    ].copy()

    indices = dataframe.index

    (
        X_train,
        X_test,
        y_train,
        y_test,
        _train_indices,
        test_indices,
    ) = train_test_split(
        X,
        y,
        indices,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    model = build_baseline_pipeline()

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

    results = (
        dataframe
        .loc[test_indices]
        .copy()
    )

    results[
        "predicted_label"
    ] = predictions

    results[
        "secret_probability"
    ] = probabilities

    false_positives = results[
        (
            results["label"] == 0
        )
        & (
            results[
                "predicted_label"
            ] == 1
        )
    ].copy()

    false_negatives = results[
        (
            results["label"] == 1
        )
        & (
            results[
                "predicted_label"
            ] == 0
        )
    ].copy()

    true_positives = results[
        (
            results["label"] == 1
        )
        & (
            results[
                "predicted_label"
            ] == 1
        )
    ].copy()

    true_negatives = results[
        (
            results["label"] == 0
        )
        & (
            results[
                "predicted_label"
            ] == 0
        )
    ].copy()

    return {
        "model": model,
        "results": results,
        "false_positives": (
            false_positives
        ),
        "false_negatives": (
            false_negatives
        ),
        "true_positives": (
            true_positives
        ),
        "true_negatives": (
            true_negatives
        ),
    }


def get_error_type_distribution(
    errors: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count errors grouped by sample type.
    """

    if errors.empty:

        return pd.DataFrame(
            columns=[
                "sample_type",
                "count",
            ]
        )

    return (
        errors[
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


def get_model_coefficients(
    model,
) -> pd.DataFrame:
    """
    Return Logistic Regression feature
    coefficients sorted by absolute impact.
    """

    classifier = (
        model.named_steps[
            "classifier"
        ]
    )

    coefficients = (
        classifier.coef_[0]
    )

    dataframe = pd.DataFrame(
        {
            "feature": (
                FEATURE_COLUMNS
            ),
            "coefficient": (
                coefficients
            ),
        }
    )

    dataframe[
        "absolute_coefficient"
    ] = (
        dataframe[
            "coefficient"
        ].abs()
    )

    return (
        dataframe
        .sort_values(
            "absolute_coefficient",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )