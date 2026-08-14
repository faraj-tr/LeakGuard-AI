from pathlib import Path

import pandas as pd

from leakguard.ml.generalization import (
    evaluate_numerical_generalization,
    evaluate_text_generalization,
)
from leakguard.ml.hybrid import (
    evaluate_hybrid_generalization,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

CHALLENGE_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def print_model(
    result,
):
    """
    Print evaluation metrics for one model.
    """

    print()
    print(
        result.model_name
    )
    print(
        "-" * 60
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

    print(
        f"False Positives: "
        f"{result.false_positives}"
    )

    print(
        f"False Negatives: "
        f"{result.false_negatives}"
    )


def main():
    """
    Compare all three LeakGuard ML models
    on Challenge Dataset v1.
    """

    if not TRAINING_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: "
            f"{TRAINING_PATH}"
        )

    if not CHALLENGE_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: "
            f"{CHALLENGE_PATH}"
        )

    training = pd.read_csv(
        TRAINING_PATH
    )

    challenge = pd.read_csv(
        CHALLENGE_PATH
    )

    numerical = (
        evaluate_numerical_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    text = (
        evaluate_text_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    hybrid = (
        evaluate_hybrid_generalization(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    print()
    print(
        "LeakGuard Hybrid Benchmark"
    )
    print(
        "=" * 60
    )

    print()
    print(
        "Training:"
    )

    print(
        "Synthetic Dataset v2 "
        f"({len(training)} samples)"
    )

    print()
    print(
        "Evaluation:"
    )

    print(
        "Challenge Dataset v1 "
        f"({len(challenge)} samples)"
    )

    print()
    print(
        "Challenge data was NOT used "
        "during training."
    )

    print_model(
        numerical
    )

    print_model(
        text
    )

    print_model(
        hybrid
    )

    print()
    print(
        "Model Comparison"
    )
    print(
        "=" * 60
    )

    print(
        f"{'Metric':<18}"
        f"{'Numerical':>13}"
        f"{'TF-IDF':>13}"
        f"{'Hybrid':>13}"
    )

    print(
        "-" * 57
    )

    print(
        f"{'Accuracy':<18}"
        f"{numerical.accuracy:>13.4f}"
        f"{text.accuracy:>13.4f}"
        f"{hybrid.accuracy:>13.4f}"
    )

    print(
        f"{'Precision':<18}"
        f"{numerical.precision:>13.4f}"
        f"{text.precision:>13.4f}"
        f"{hybrid.precision:>13.4f}"
    )

    print(
        f"{'Recall':<18}"
        f"{numerical.recall:>13.4f}"
        f"{text.recall:>13.4f}"
        f"{hybrid.recall:>13.4f}"
    )

    print(
        f"{'F1':<18}"
        f"{numerical.f1:>13.4f}"
        f"{text.f1:>13.4f}"
        f"{hybrid.f1:>13.4f}"
    )

    print(
        f"{'ROC AUC':<18}"
        f"{numerical.roc_auc:>13.4f}"
        f"{text.roc_auc:>13.4f}"
        f"{hybrid.roc_auc:>13.4f}"
    )

    print(
        f"{'False Positives':<18}"
        f"{numerical.false_positives:>13}"
        f"{text.false_positives:>13}"
        f"{hybrid.false_positives:>13}"
    )

    print(
        f"{'False Negatives':<18}"
        f"{numerical.false_negatives:>13}"
        f"{text.false_negatives:>13}"
        f"{hybrid.false_negatives:>13}"
    )

    print()


if __name__ == "__main__":
    main()