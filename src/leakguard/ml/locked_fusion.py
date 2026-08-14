import pandas as pd

from leakguard.ml.challenge_analysis import (
    build_challenge_predictions,
)
from leakguard.ml.fusion import (
    FusionResult,
    evaluate_fusion_configuration,
)


LOCKED_TEXT_WEIGHT = 0.60
LOCKED_NUMERICAL_WEIGHT = 0.40
LOCKED_THRESHOLD = 0.40

LOCKED_MODEL_NAME = (
    "LeakGuard Fusion Candidate v1"
)


def evaluate_locked_fusion(
    training_dataframe: pd.DataFrame,
    evaluation_dataframe: pd.DataFrame,
) -> FusionResult:
    """
    Evaluate the locked LeakGuard fusion
    configuration.

    IMPORTANT:
    The weights and threshold in this file
    were selected using Challenge Dataset v1.

    They must not be changed after observing
    results from a final evaluation dataset.
    """

    predictions = (
        build_challenge_predictions(
            training_dataframe=(
                training_dataframe
            ),
            challenge_dataframe=(
                evaluation_dataframe
            ),
        )
    )

    return (
        evaluate_fusion_configuration(
            results=predictions,
            text_weight=(
                LOCKED_TEXT_WEIGHT
            ),
            threshold=(
                LOCKED_THRESHOLD
            ),
        )
    )


def get_locked_configuration() -> dict:
    """
    Return the frozen LeakGuard Fusion
    Candidate v1 configuration.
    """

    return {
        "model_name": (
            LOCKED_MODEL_NAME
        ),
        "text_weight": (
            LOCKED_TEXT_WEIGHT
        ),
        "numerical_weight": (
            LOCKED_NUMERICAL_WEIGHT
        ),
        "threshold": (
            LOCKED_THRESHOLD
        ),
    }