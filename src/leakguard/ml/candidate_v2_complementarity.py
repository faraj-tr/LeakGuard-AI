import pandas as pd

from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)
from sklearn.linear_model import (
    LogisticRegression,
)
from sklearn.pipeline import Pipeline

from leakguard.ml.generalization import (
    GeneralizationResult,
    calculate_metrics,
)
from leakguard.ml.text_baseline import (
    validate_text_dataframe,
)


def build_text_input(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """
    Build lexical Candidate v2 inputs using
    only variable_name and value.

    Dataset metadata such as sample_type,
    source, and framework is never used as
    a model feature.
    """

    validate_text_dataframe(
        dataframe
    )

    variable_names = (
        dataframe[
            "variable_name"
        ]
        .fillna("")
        .astype(str)
    )

    values = (
        dataframe[
            "value"
        ]
        .fillna("")
        .astype(str)
    )

    return (
        variable_names
        + " = "
        + values
    )


def build_text_probe_pipeline() -> Pipeline:
    """
    Build Candidate v2 lexical probe.

    This is an experiment, not a locked
    production model.
    """

    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=(
                        3,
                        5,
                    ),
                    min_df=2,
                    sublinear_tf=True,
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


def fit_text_probe(
    training_dataframe: pd.DataFrame,
) -> Pipeline:
    """
    Fit lexical Candidate v2 probe.
    """

    X_train = build_text_input(
        training_dataframe
    )

    y_train = training_dataframe[
        "label"
    ].copy()

    model = (
        build_text_probe_pipeline()
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


def evaluate_text_probe(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> GeneralizationResult:
    """
    Train on Synthetic Dataset v3 and
    evaluate on Challenge v1 development
    data.
    """

    model = fit_text_probe(
        training_dataframe
    )

    X_development = (
        build_text_input(
            development_dataframe
        )
    )

    predictions = model.predict(
        X_development
    )

    probabilities = (
        model.predict_proba(
            X_development
        )[:, 1]
    )

    return calculate_metrics(
        model_name=(
            "Candidate v2 TF-IDF "
            "Lexical Probe"
        ),
        y_true=development_dataframe[
            "label"
        ],
        predictions=predictions,
        probabilities=probabilities,
        training_samples=len(
            training_dataframe
        ),
        challenge_samples=len(
            development_dataframe
        ),
    )


def build_text_predictions(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return development predictions from
    the Candidate v2 lexical probe.
    """

    model = fit_text_probe(
        training_dataframe
    )

    X_development = (
        build_text_input(
            development_dataframe
        )
    )

    results = (
        development_dataframe
        .copy()
        .reset_index(
            drop=True
        )
    )

    results[
        "text_prediction"
    ] = model.predict(
        X_development
    )

    results[
        "text_probability"
    ] = model.predict_proba(
        X_development
    )[:, 1]

    return results


def build_complementarity_frame(
    context_results: pd.DataFrame,
    text_results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare contextual and lexical model
    decisions on identical development rows.
    """

    if len(
        context_results
    ) != len(
        text_results
    ):
        raise ValueError(
            "Prediction frames must "
            "have equal length."
        )

    context_labels = (
        context_results[
            "label"
        ]
        .reset_index(
            drop=True
        )
    )

    text_labels = (
        text_results[
            "label"
        ]
        .reset_index(
            drop=True
        )
    )

    if not context_labels.equals(
        text_labels
    ):
        raise ValueError(
            "Prediction frames must "
            "contain identical labels."
        )

    results = (
        context_results
        .copy()
        .reset_index(
            drop=True
        )
    )

    results[
        "text_prediction"
    ] = (
        text_results[
            "text_prediction"
        ]
        .reset_index(
            drop=True
        )
    )

    results[
        "text_probability"
    ] = (
        text_results[
            "text_probability"
        ]
        .reset_index(
            drop=True
        )
    )

    results[
        "context_correct"
    ] = (
        results[
            "context_prediction"
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

    outcomes = []

    for row in results[
        [
            "context_correct",
            "text_correct",
        ]
    ].itertuples(
        index=False
    ):

        if (
            row.context_correct
            and row.text_correct
        ):
            outcomes.append(
                "both_correct"
            )

        elif (
            row.context_correct
            and not row.text_correct
        ):
            outcomes.append(
                "context_only_correct"
            )

        elif (
            not row.context_correct
            and row.text_correct
        ):
            outcomes.append(
                "text_only_correct"
            )

        else:
            outcomes.append(
                "both_wrong"
            )

    results[
        "outcome"
    ] = outcomes

    return results


def get_outcome_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize complementarity outcomes.
    """

    return (
        dataframe[
            "outcome"
        ]
        .value_counts()
        .rename_axis(
            "outcome"
        )
        .reset_index(
            name="count"
        )
    )


def get_type_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Group selected development examples
    by diagnostic sample_type.

    sample_type is never a model feature.
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
