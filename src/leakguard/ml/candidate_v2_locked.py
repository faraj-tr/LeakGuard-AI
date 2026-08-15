import pandas as pd

from leakguard.ml.candidate_v2_fusion import (
    build_candidate_v2_probability_frame,
    build_fusion_decisions,
)
from leakguard.ml.generalization import (
    calculate_metrics,
)


LOCKED_TEXT_WEIGHT = 0.70
LOCKED_CONTEXT_WEIGHT = 0.30
LOCKED_THRESHOLD = 0.50

MINIMUM_DEVELOPMENT_RECALL = 0.98

SELECTION_POLICY = (
    "Require recall >= 0.98, then maximize "
    "precision, then F1, then minimize "
    "false positives."
)


def validate_locked_configuration() -> None:
    """
    Protect the Candidate v2 configuration
    selected before holdout evaluation.
    """

    if (
        abs(
            (
                LOCKED_TEXT_WEIGHT
                + LOCKED_CONTEXT_WEIGHT
            )
            - 1.0
        )
        > 1e-12
    ):
        raise ValueError(
            "Locked fusion weights must "
            "sum to 1.0."
        )

    if not (
        0.0
        <= LOCKED_THRESHOLD
        <= 1.0
    ):
        raise ValueError(
            "Locked threshold must be "
            "between 0 and 1."
        )


def build_locked_candidate_v2_decisions(
    training_dataframe: pd.DataFrame,
    evaluation_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run the locked Candidate v2 late fusion.

    No evaluation-set tuning is performed.
    """

    validate_locked_configuration()

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=(
                training_dataframe
            ),
            development_dataframe=(
                evaluation_dataframe
            ),
        )
    )

    return build_fusion_decisions(
        probability_frame=probabilities,
        text_weight=(
            LOCKED_TEXT_WEIGHT
        ),
        threshold=(
            LOCKED_THRESHOLD
        ),
    )


def evaluate_locked_candidate_v2(
    training_dataframe: pd.DataFrame,
    evaluation_dataframe: pd.DataFrame,
):
    """
    Evaluate the locked Candidate v2
    configuration on supplied data.

    The caller is responsible for ensuring
    the evaluation set has not been used
    for training or tuning.
    """

    decisions = (
        build_locked_candidate_v2_decisions(
            training_dataframe=(
                training_dataframe
            ),
            evaluation_dataframe=(
                evaluation_dataframe
            ),
        )
    )

    return calculate_metrics(
        model_name=(
            "LeakGuard Candidate v2 "
            "Locked Late Fusion"
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
        training_samples=len(
            training_dataframe
        ),
        challenge_samples=len(
            evaluation_dataframe
        ),
    )
