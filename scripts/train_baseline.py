from pathlib import Path

import pandas as pd

from leakguard.ml.baseline import (
    FEATURE_COLUMNS,
    train_baseline,
)


DATASET_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)


def main():
    """
    Train and evaluate LeakGuard
    Numerical Baseline v1.
    """

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            "Dataset not found: "
            f"{DATASET_PATH}"
        )

    dataframe = pd.read_csv(
        DATASET_PATH
    )

    result = train_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    print()
    print(
        "LeakGuard ML Baseline v1"
    )
    print(
        "=" * 44
    )

    print()
    print(
        "Model"
    )
    print(
        "-" * 44
    )

    print(
        "Algorithm: Logistic Regression"
    )

    print(
        "Preprocessing: StandardScaler"
    )

    print(
        "Dataset: Synthetic Dataset v2"
    )

    print(
        "Split: 80% train / 20% test"
    )

    print()
    print(
        "Features"
    )
    print(
        "-" * 44
    )

    for feature in FEATURE_COLUMNS:
        print(
            f"- {feature}"
        )

    print()
    print(
        "Dataset Split"
    )
    print(
        "-" * 44
    )

    print(
        f"Training samples: "
        f"{result.train_samples}"
    )

    print(
        f"Testing samples: "
        f"{result.test_samples}"
    )

    print()
    print(
        "Evaluation"
    )
    print(
        "-" * 44
    )

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
        "Confusion Matrix"
    )
    print(
        "-" * 44
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

    print(
        f"True Positives:  "
        f"{result.true_positives}"
    )

    print()


if __name__ == "__main__":
    main()