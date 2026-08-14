from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from leakguard.ml.challenge_analysis import (
    build_challenge_predictions,
)


@dataclass
class FusionResult:
    """
    Store one late-fusion configuration
    and its evaluation metrics.
    """

    text_weight: float
    numerical_weight: float
    threshold: float

    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

    false_positives: int
    false_negatives: int
    true_positives: int
    true_negatives: int


def calculate_fusion_probability(
    numerical_probability,
    text_probability,
    text_weight: float,
):
    """
    Combine model probabilities using
    weighted late fusion.

    numerical_weight = 1 - text_weight
    """

    if not 0.0 <= text_weight <= 1.0:
        raise ValueError(
            "text_weight must be between "
            "0 and 1."
        )

    numerical_weight = (
        1.0 - text_weight
    )

    return (
        numerical_weight
        * np.asarray(
            numerical_probability
        )
        + text_weight
        * np.asarray(
            text_probability
        )
    )


def evaluate_fusion_configuration(
    results: pd.DataFrame,
    text_weight: float,
    threshold: float,
) -> FusionResult:
    """
    Evaluate one probability-fusion
    configuration.
    """

    if not 0.0 < threshold < 1.0:
        raise ValueError(
            "threshold must be between "
            "0 and 1."
        )

    probabilities = (
        calculate_fusion_probability(
            numerical_probability=results[
                "numerical_probability"
            ],
            text_probability=results[
                "text_probability"
            ],
            text_weight=text_weight,
        )
    )

    predictions = (
        probabilities
        >= threshold
    ).astype(int)

    labels = (
        results["label"]
        .to_numpy()
    )

    true_positive = int(
        (
            (labels == 1)
            & (predictions == 1)
        ).sum()
    )

    true_negative = int(
        (
            (labels == 0)
            & (predictions == 0)
        ).sum()
    )

    false_positive = int(
        (
            (labels == 0)
            & (predictions == 1)
        ).sum()
    )

    false_negative = int(
        (
            (labels == 1)
            & (predictions == 0)
        ).sum()
    )

    return FusionResult(
        text_weight=text_weight,
        numerical_weight=(
            1.0 - text_weight
        ),
        threshold=threshold,

        accuracy=float(
            accuracy_score(
                labels,
                predictions,
            )
        ),

        precision=float(
            precision_score(
                labels,
                predictions,
                zero_division=0,
            )
        ),

        recall=float(
            recall_score(
                labels,
                predictions,
                zero_division=0,
            )
        ),

        f1=float(
            f1_score(
                labels,
                predictions,
                zero_division=0,
            )
        ),

        roc_auc=float(
            roc_auc_score(
                labels,
                probabilities,
            )
        ),

        false_positives=(
            false_positive
        ),

        false_negatives=(
            false_negative
        ),

        true_positives=(
            true_positive
        ),

        true_negatives=(
            true_negative
        ),
    )


def search_fusion_configurations(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Search a small, explicit grid of
    late-fusion weights and thresholds.

    IMPORTANT:
    This function is for development data,
    not the final untouched test set.
    """

    predictions = (
        build_challenge_predictions(
            training_dataframe=(
                training_dataframe
            ),
            challenge_dataframe=(
                development_dataframe
            ),
        )
    )

    text_weights = [
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
    ]

    thresholds = [
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
    ]

    records = []

    for text_weight in text_weights:

        for threshold in thresholds:

            result = (
                evaluate_fusion_configuration(
                    results=predictions,
                    text_weight=text_weight,
                    threshold=threshold,
                )
            )

            records.append(
                {
                    "text_weight": (
                        result.text_weight
                    ),
                    "numerical_weight": (
                        result.numerical_weight
                    ),
                    "threshold": (
                        result.threshold
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
                    "f1": (
                        result.f1
                    ),
                    "roc_auc": (
                        result.roc_auc
                    ),
                    "false_positives": (
                        result.false_positives
                    ),
                    "false_negatives": (
                        result.false_negatives
                    ),
                }
            )

    return pd.DataFrame(
        records
    )


def rank_security_configurations(
    dataframe: pd.DataFrame,
    minimum_recall: float = 0.85,
) -> pd.DataFrame:
    """
    Rank configurations suitable for a
    security gate.

    First require acceptable recall.
    Then prioritize F1 and fewer false
    negatives.
    """

    candidates = dataframe[
        dataframe["recall"]
        >= minimum_recall
    ].copy()

    if candidates.empty:
        candidates = (
            dataframe.copy()
        )

    return (
        candidates
        .sort_values(
            by=[
                "f1",
                "false_negatives",
                "precision",
            ],
            ascending=[
                False,
                True,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )