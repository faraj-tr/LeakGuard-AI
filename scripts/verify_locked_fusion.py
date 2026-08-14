from pathlib import Path

import pandas as pd

from leakguard.ml.locked_fusion import (
    get_locked_configuration,
    evaluate_locked_fusion,
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
    Verify the frozen LeakGuard Fusion
    Candidate v1 configuration on the
    development dataset.

    Challenge v1 is NOT a final test set.
    """

    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    configuration = (
        get_locked_configuration()
    )

    result = (
        evaluate_locked_fusion(
            training_dataframe=training,
            evaluation_dataframe=(
                development
            ),
        )
    )

    print()
    print(
        "LeakGuard Locked Fusion Candidate"
    )
    print(
        "=" * 56
    )

    print()
    print(
        f"Model: "
        f"{configuration['model_name']}"
    )

    print(
        f"Text weight: "
        f"{configuration['text_weight']:.2f}"
    )

    print(
        f"Numerical weight: "
        f"{configuration['numerical_weight']:.2f}"
    )

    print(
        f"Threshold: "
        f"{configuration['threshold']:.2f}"
    )

    print()
    print(
        "Development Verification"
    )
    print(
        "-" * 56
    )

    print(
        "Dataset: Challenge Dataset v1"
    )

    print(
        "Status: DEVELOPMENT DATASET"
    )

    print()
    print(
        f"Accuracy:  "
        f"{result.accuracy:.4f}"
    )

    print(
        f"Precision: "
        f"{result.precision:.4f}"
    )

    print(
        f"Recall:    "
        f"{result.recall:.4f}"
    )

    print(
        f"F1 Score:  "
        f"{result.f1:.4f}"
    )

    print(
        f"ROC AUC:   "
        f"{result.roc_auc:.4f}"
    )

    print()
    print(
        f"True Positives:  "
        f"{result.true_positives}"
    )

    print(
        f"True Negatives:  "
        f"{result.true_negatives}"
    )

    print(
        f"False Positives: "
        f"{result.false_positives}"
    )

    print(
        f"False Negatives: "
        f"{result.false_negatives}"
    )

    print()
    print(
        "CONFIGURATION LOCKED"
    )

    print(
        "Do not tune weights or threshold "
        "using the final challenge dataset."
    )

    print()


if __name__ == "__main__":
    main()