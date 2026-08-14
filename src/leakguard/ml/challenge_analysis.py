import pandas as pd

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


def build_challenge_predictions(
    training_dataframe: pd.DataFrame,
    challenge_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Train both LeakGuard baseline models
    using Synthetic Dataset v2 only and
    generate predictions for the independent
    Challenge Dataset v1.
    """

    validate_training_dataframe(
        training_dataframe
    )

    validate_training_dataframe(
        challenge_dataframe
    )

    validate_text_dataframe(
        training_dataframe
    )

    validate_text_dataframe(
        challenge_dataframe
    )

    # =====================================
    # Numerical model
    # =====================================

    numerical_model = (
        build_baseline_pipeline()
    )

    numerical_model.fit(
        training_dataframe[
            FEATURE_COLUMNS
        ],
        training_dataframe[
            "label"
        ],
    )

    numerical_predictions = (
        numerical_model.predict(
            challenge_dataframe[
                FEATURE_COLUMNS
            ]
        )
    )

    numerical_probabilities = (
        numerical_model.predict_proba(
            challenge_dataframe[
                FEATURE_COLUMNS
            ]
        )[:, 1]
    )

    # =====================================
    # TF-IDF text model
    # =====================================

    text_model = (
        build_text_pipeline()
    )

    text_model.fit(
        build_candidate_text(
            training_dataframe
        ),
        training_dataframe[
            "label"
        ],
    )

    text_predictions = (
        text_model.predict(
            build_candidate_text(
                challenge_dataframe
            )
        )
    )

    text_probabilities = (
        text_model.predict_proba(
            build_candidate_text(
                challenge_dataframe
            )
        )[:, 1]
    )

    # =====================================
    # Combined result table
    # =====================================

    results = (
        challenge_dataframe
        .copy()
        .reset_index(
            drop=True
        )
    )

    results[
        "numerical_prediction"
    ] = numerical_predictions

    results[
        "numerical_probability"
    ] = numerical_probabilities

    results[
        "text_prediction"
    ] = text_predictions

    results[
        "text_probability"
    ] = text_probabilities

    results[
        "numerical_correct"
    ] = (
        results[
            "numerical_prediction"
        ]
        == results["label"]
    )

    results[
        "text_correct"
    ] = (
        results[
            "text_prediction"
        ]
        == results["label"]
    )

    return results


def get_model_errors(
    results: pd.DataFrame,
    prediction_column: str,
    error_type: str,
) -> pd.DataFrame:
    """
    Extract false positives or false
    negatives for one prediction column.
    """

    if error_type == "false_positive":

        return results[
            (
                results["label"]
                == 0
            )
            & (
                results[
                    prediction_column
                ]
                == 1
            )
        ].copy()

    if error_type == "false_negative":

        return results[
            (
                results["label"]
                == 1
            )
            & (
                results[
                    prediction_column
                ]
                == 0
            )
        ].copy()

    raise ValueError(
        "error_type must be "
        "'false_positive' or "
        "'false_negative'."
    )


def get_type_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count samples grouped by sample_type.
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


def get_agreement_summary(
    results: pd.DataFrame,
) -> dict:
    """
    Compare whether the numerical and
    text models succeed on the same samples.
    """

    both_correct = int(
        (
            results[
                "numerical_correct"
            ]
            & results[
                "text_correct"
            ]
        ).sum()
    )

    both_wrong = int(
        (
            ~results[
                "numerical_correct"
            ]
            & ~results[
                "text_correct"
            ]
        ).sum()
    )

    numerical_only_correct = int(
        (
            results[
                "numerical_correct"
            ]
            & ~results[
                "text_correct"
            ]
        ).sum()
    )

    text_only_correct = int(
        (
            ~results[
                "numerical_correct"
            ]
            & results[
                "text_correct"
            ]
        ).sum()
    )

    return {
        "both_correct": (
            both_correct
        ),
        "both_wrong": (
            both_wrong
        ),
        "numerical_only_correct": (
            numerical_only_correct
        ),
        "text_only_correct": (
            text_only_correct
        ),
    }


def get_text_fixed_numerical_secrets(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return real secrets missed by the
    numerical model but detected by TF-IDF.
    """

    return results[
        (
            results["label"] == 1
        )
        & (
            results[
                "numerical_prediction"
            ] == 0
        )
        & (
            results[
                "text_prediction"
            ] == 1
        )
    ].copy()


def get_numerical_fixed_text_safe_samples(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return safe samples falsely flagged by
    TF-IDF but correctly handled by the
    numerical model.
    """

    return results[
        (
            results["label"] == 0
        )
        & (
            results[
                "text_prediction"
            ] == 1
        )
        & (
            results[
                "numerical_prediction"
            ] == 0
        )
    ].copy()