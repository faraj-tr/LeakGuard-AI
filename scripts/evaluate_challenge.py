from pathlib import Path

import pandas as pd

from leakguard.ml.generalization import (
    evaluate_numerical_generalization,
    evaluate_text_generalization,
)


TRAINING_DATASET_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

CHALLENGE_DATASET_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def print_result(
    result,
):
    """
    Print one challenge evaluation result.
    """

    print()
    print(
        result.model_name
    )
    print(
        "-" * 54
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


def main():
    """
    Evaluate LeakGuard baseline models on
    an independent out-of-distribution
    challenge dataset.
    """

    if not TRAINING_DATASET_PATH.exists():
        raise FileNotFoundError(
            "Training dataset not found: "
            f"{TRAINING_DATASET_PATH}"
        )

    if not CHALLENGE_DATASET_PATH.exists():
        raise FileNotFoundError(
            "Challenge dataset not found: "
            f"{CHALLENGE_DATASET_PATH}"
        )

    training_dataframe = pd.read_csv(
        TRAINING_DATASET_PATH
    )

    challenge_dataframe = pd.read_csv(
        CHALLENGE_DATASET_PATH
    )

    numerical_result = (
        evaluate_numerical_generalization(
            training_dataframe=(
                training_dataframe
            ),
            challenge_dataframe=(
                challenge_dataframe
            ),
        )
    )

    text_result = (
        evaluate_text_generalization(
            training_dataframe=(
                training_dataframe
            ),
            challenge_dataframe=(
                challenge_dataframe
            ),
        )
    )

    print()
    print(
        "LeakGuard Generalization Benchmark"
    )
    print(
        "=" * 54
    )

    print()
    print(
        "Training Dataset:"
    )

    print(
        "  Synthetic Dataset v2"
    )

    print(
        f"  Samples: "
        f"{len(training_dataframe)}"
    )

    print()
    print(
        "Evaluation Dataset:"
    )

    print(
        "  Challenge Dataset v1"
    )

    print(
        f"  Samples: "
        f"{len(challenge_dataframe)}"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Challenge samples were not used "
        "for model training."
    )

    print_result(
        numerical_result
    )

    print_result(
        text_result
    )

    print()
    print(
        "Comparison"
    )
    print(
        "=" * 54
    )

    print(
        f"{'Metric':<14}"
        f"{'Numerical':>14}"
        f"{'TF-IDF':>14}"
    )

    print(
        "-" * 42
    )

    print(
        f"{'Accuracy':<14}"
        f"{numerical_result.accuracy:>14.4f}"
        f"{text_result.accuracy:>14.4f}"
    )

    print(
        f"{'Precision':<14}"
        f"{numerical_result.precision:>14.4f}"
        f"{text_result.precision:>14.4f}"
    )

    print(
        f"{'Recall':<14}"
        f"{numerical_result.recall:>14.4f}"
        f"{text_result.recall:>14.4f}"
    )

    print(
        f"{'F1':<14}"
        f"{numerical_result.f1:>14.4f}"
        f"{text_result.f1:>14.4f}"
    )

    print(
        f"{'ROC AUC':<14}"
        f"{numerical_result.roc_auc:>14.4f}"
        f"{text_result.roc_auc:>14.4f}"
    )

    print()


if __name__ == "__main__":
    main()