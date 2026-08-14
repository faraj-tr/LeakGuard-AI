from pathlib import Path

import pandas as pd

from leakguard.ml.fusion import (
    rank_security_configurations,
    search_fusion_configurations,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

DEVELOPMENT_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def main():
    """
    Tune LeakGuard late fusion on the
    OOD development set.

    Challenge v1 is now treated as
    development data because its results
    have already been inspected.
    """

    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    results = (
        search_fusion_configurations(
            training_dataframe=training,
            development_dataframe=(
                development
            ),
        )
    )

    ranked = (
        rank_security_configurations(
            results,
            minimum_recall=0.85,
        )
    )

    print()
    print(
        "LeakGuard Late Fusion Tuning"
    )
    print(
        "=" * 68
    )

    print()
    print(
        "Training Dataset:"
    )
    print(
        "Synthetic Dataset v2"
    )

    print()
    print(
        "Development Dataset:"
    )
    print(
        "Challenge Dataset v1"
    )

    print()
    print(
        "IMPORTANT:"
    )
    print(
        "Challenge v1 is development data "
        "from this point forward."
    )

    print()
    print(
        "Top Security Configurations"
    )
    print(
        "-" * 68
    )

    columns = [
        "text_weight",
        "numerical_weight",
        "threshold",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "false_positives",
        "false_negatives",
    ]

    print(
        ranked[
            columns
        ]
        .head(15)
        .to_string(
            index=False
        )
    )

    print()


if __name__ == "__main__":
    main()