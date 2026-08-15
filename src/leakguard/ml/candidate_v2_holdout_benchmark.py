import json
from pathlib import Path

import pandas as pd

from leakguard.ml.candidate_v2_holdout_gate import (
    EXPECTED_HOLDOUT_SHA256,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
    MINIMUM_DEVELOPMENT_RECALL,
    SELECTION_POLICY,
    build_locked_candidate_v2_decisions,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_DEVELOPMENT_SHA256,
    EXPECTED_TRAINING_SHA256,
)
from leakguard.ml.generalization import (
    calculate_metrics,
)


BENCHMARK_NAME = (
    "LeakGuard Candidate v2 "
    "Independent Holdout Benchmark v1"
)


def build_candidate_v2_holdout_report(
    training_dataframe: pd.DataFrame,
    holdout_dataframe: pd.DataFrame,
) -> dict:
    """
    Evaluate the already-locked Candidate v2
    configuration on the independent holdout.

    No parameter search, threshold tuning,
    feature tuning, or error-family analysis
    is performed here.
    """

    decisions = (
        build_locked_candidate_v2_decisions(
            training_dataframe=(
                training_dataframe
            ),
            evaluation_dataframe=(
                holdout_dataframe
            ),
        )
    )

    result = calculate_metrics(
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
            holdout_dataframe
        ),
    )

    false_positives = int(
        result.false_positives
    )

    false_negatives = int(
        result.false_negatives
    )

    total_positive = int(
        (
            holdout_dataframe[
                "label"
            ]
            == 1
        ).sum()
    )

    total_negative = int(
        (
            holdout_dataframe[
                "label"
            ]
            == 0
        ).sum()
    )

    true_positives = (
        total_positive
        - false_negatives
    )

    true_negatives = (
        total_negative
        - false_positives
    )

    return {
        "benchmark_name": (
            BENCHMARK_NAME
        ),
        "model": (
            "LeakGuard Candidate v2 "
            "Locked Late Fusion"
        ),
        "datasets": {
            "training": {
                "samples": len(
                    training_dataframe
                ),
                "source": "synthetic_v3",
                "sha256": (
                    EXPECTED_TRAINING_SHA256
                ),
            },
            "development": {
                "samples": 600,
                "source": (
                    "candidate_v2_dev_v1"
                ),
                "sha256": (
                    EXPECTED_DEVELOPMENT_SHA256
                ),
                "purpose": (
                    "development and "
                    "fusion tuning only"
                ),
            },
            "holdout": {
                "samples": len(
                    holdout_dataframe
                ),
                "source": (
                    "candidate_v2_holdout_v1"
                ),
                "sha256": (
                    EXPECTED_HOLDOUT_SHA256
                ),
                "purpose": (
                    "independent locked "
                    "evaluation only"
                ),
            },
        },
        "locked_configuration": {
            "text_weight": (
                LOCKED_TEXT_WEIGHT
            ),
            "context_weight": (
                LOCKED_CONTEXT_WEIGHT
            ),
            "threshold": (
                LOCKED_THRESHOLD
            ),
            "minimum_development_recall": (
                MINIMUM_DEVELOPMENT_RECALL
            ),
            "selection_policy": (
                SELECTION_POLICY
            ),
        },
        "evaluation_policy": {
            "holdout_used_for_training": (
                False
            ),
            "holdout_used_for_tuning": (
                False
            ),
            "parameters_locked_before_holdout": (
                True
            ),
            "final_challenge_v2_used": (
                False
            ),
            "do_not_retune_from_holdout": (
                True
            ),
        },
        "metrics": {
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
            "true_positives": (
                true_positives
            ),
            "true_negatives": (
                true_negatives
            ),
            "false_positives": (
                false_positives
            ),
            "false_negatives": (
                false_negatives
            ),
        },
    }


def save_candidate_v2_holdout_report(
    report: dict,
    output_path: Path,
) -> None:
    """
    Save the one-shot holdout benchmark.

    Existing reports are never overwritten.
    """

    if output_path.exists():
        raise FileExistsError(
            "Candidate v2 holdout report "
            f"already exists: {output_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
