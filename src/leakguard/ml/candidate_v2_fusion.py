import pandas as pd

from leakguard.ml.candidate_v2_complementarity import (
    build_text_input,
    fit_text_probe,
)
from leakguard.ml.context_baseline import (
    build_context_feature_frame,
    fit_context_model,
)
from leakguard.ml.generalization import (
    calculate_metrics,
)


DEFAULT_TEXT_WEIGHTS = (
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
)


DEFAULT_THRESHOLDS = (
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
)


def validate_fusion_parameters(
    text_weight: float,
    threshold: float,
) -> None:
    """
    Validate Candidate v2 fusion settings.
    """

    if not 0.0 <= text_weight <= 1.0:
        raise ValueError(
            "text_weight must be between "
            "0.0 and 1.0."
        )

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must be between "
            "0.0 and 1.0."
        )


def build_candidate_v2_probability_frame(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Train Candidate v2 Context and Text
    models on Synthetic Dataset v3 and
    return their probabilities on the
    development set.

    Dataset metadata is preserved only for
    diagnostics. It is never used as model
    input.
    """

    context_model = fit_context_model(
        training_dataframe
    )

    text_model = fit_text_probe(
        training_dataframe
    )

    context_features = (
        build_context_feature_frame(
            development_dataframe
        )
    )

    text_input = build_text_input(
        development_dataframe
    )

    context_probabilities = (
        context_model.predict_proba(
            context_features
        )[:, 1]
    )

    text_probabilities = (
        text_model.predict_proba(
            text_input
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
        "context_probability"
    ] = context_probabilities

    results[
        "text_probability"
    ] = text_probabilities

    return results


def build_fusion_decisions(
    probability_frame: pd.DataFrame,
    text_weight: float,
    threshold: float,
) -> pd.DataFrame:
    """
    Blend Text and Context probabilities.

    context_weight is always:
        1.0 - text_weight
    """

    validate_fusion_parameters(
        text_weight=text_weight,
        threshold=threshold,
    )

    required_columns = {
        "label",
        "context_probability",
        "text_probability",
    }

    missing = (
        required_columns
        - set(
            probability_frame.columns
        )
    )

    if missing:
        raise ValueError(
            "Missing probability columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    context_weight = (
        1.0 - text_weight
    )

    results = (
        probability_frame
        .copy()
        .reset_index(
            drop=True
        )
    )

    results[
        "fusion_probability"
    ] = (
        text_weight
        * results[
            "text_probability"
        ]
        + context_weight
        * results[
            "context_probability"
        ]
    )

    results[
        "fusion_prediction"
    ] = (
        results[
            "fusion_probability"
        ]
        >= threshold
    ).astype(int)

    return results


def evaluate_candidate_v2_fusion(
    probability_frame: pd.DataFrame,
    text_weight: float,
    threshold: float,
    training_samples: int,
):
    """
    Evaluate one Candidate v2 late-fusion
    configuration on development data.
    """

    decisions = (
        build_fusion_decisions(
            probability_frame=(
                probability_frame
            ),
            text_weight=text_weight,
            threshold=threshold,
        )
    )

    context_weight = (
        1.0 - text_weight
    )

    return calculate_metrics(
        model_name=(
            "Candidate v2 Late Fusion "
            f"(text={text_weight:.2f}, "
            f"context={context_weight:.2f}, "
            f"threshold={threshold:.2f})"
        ),
        y_true=decisions[
            "label"
        ],
        predictions=decisions[
            "fusion_prediction"
        ],
        probabilities=decisions[
            "fusion_probability"
        ],
        training_samples=(
            training_samples
        ),
        challenge_samples=len(
            decisions
        ),
    )


def search_candidate_v2_fusion(
    probability_frame: pd.DataFrame,
    training_samples: int,
    text_weights=(
        DEFAULT_TEXT_WEIGHTS
    ),
    thresholds=(
        DEFAULT_THRESHOLDS
    ),
) -> pd.DataFrame:
    """
    Perform a deliberately coarse fusion
    search on the Candidate v2 development
    set.

    A coarse grid is preferred here to avoid
    pretending that tiny parameter changes
    are meaningful on synthetic development
    data.
    """

    records = []

    for text_weight in (
        text_weights
    ):

        for threshold in (
            thresholds
        ):

            result = (
                evaluate_candidate_v2_fusion(
                    probability_frame=(
                        probability_frame
                    ),
                    text_weight=(
                        text_weight
                    ),
                    threshold=threshold,
                    training_samples=(
                        training_samples
                    ),
                )
            )

            records.append(
                {
                    "text_weight": (
                        text_weight
                    ),
                    "context_weight": (
                        1.0
                        - text_weight
                    ),
                    "threshold": (
                        threshold
                    ),
                    "accuracy": (
                        result.accuracy
                    ),
                    "precision": (
                        result.precision
                    ),
                    "recall": (
                        result.recall
                    ),
                    "f1": result.f1,
                    "roc_auc": (
                        result.roc_auc
                    ),
                    "false_positives": (
                        result.false_positives
                    ),
                    "false_negatives": (
                        result.false_negatives
                    ),
                    "total_errors": (
                        result.false_positives
                        + result.false_negatives
                    ),
                }
            )

    results = pd.DataFrame(
        records
    )

    return (
        results
        .sort_values(
            by=[
                "f1",
                "recall",
                "precision",
                "accuracy",
            ],
            ascending=[
                False,
                False,
                False,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )


def get_fusion_false_negatives(
    decisions: pd.DataFrame,
) -> pd.DataFrame:
    return decisions[
        (
            decisions[
                "label"
            ]
            == 1
        )
        & (
            decisions[
                "fusion_prediction"
            ]
            == 0
        )
    ].copy()


def get_fusion_false_positives(
    decisions: pd.DataFrame,
) -> pd.DataFrame:
    return decisions[
        (
            decisions[
                "label"
            ]
            == 0
        )
        & (
            decisions[
                "fusion_prediction"
            ]
            == 1
        )
    ].copy()
