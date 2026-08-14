from pathlib import Path

import pandas as pd

from leakguard.ml.text_baseline import (
    train_text_baseline,
)


DATASET_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)


def main():
    """
    Train and evaluate LeakGuard
    TF-IDF Text Baseline v1.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "Dataset not found: "
            f"{DATASET_PATH}"
        )

    dataframe = pd.read_csv(
        DATASET_PATH
    )

    result = train_text_baseline(
        dataframe=dataframe,
        test_size=0.20,
        random_state=42,
    )

    print()
    print(
        "LeakGuard TF-IDF Text Baseline v1"
    )
    print(
        "=" * 48
    )

    print()
    print("Model")
    print("-" * 48)

    print(
        "Representation: Variable name + value"
    )

    print(
        "Vectorizer: Character TF-IDF"
    )

    print(
        "N-grams: 3 to 5 characters"
    )

    print(
        "Classifier: Logistic Regression"
    )

    print(
        "Dataset: Synthetic Dataset v2"
    )

    print(
        "Split: 80% train / 20% test"
    )

    print()
    print("Dataset Split")
    print("-" * 48)

    print(
        f"Training samples: "
        f"{result.train_samples}"
    )

    print(
        f"Testing samples: "
        f"{result.test_samples}"
    )

    print()
    print("Evaluation")
    print("-" * 48)

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
    print("Confusion Matrix")
    print("-" * 48)

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