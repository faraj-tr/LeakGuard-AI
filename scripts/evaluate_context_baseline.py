from pathlib import Path

import pandas as pd

from leakguard.ml.context_baseline import (
    evaluate_context_generalization,
    fit_context_model,
    get_context_coefficients,
)
from leakguard.ml.generalization import (
    evaluate_numerical_generalization,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

DEVELOPMENT_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def print_result(
    result,
):
    print()
    print(result.model_name)
    print("-" * 62)

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
    Compare Candidate v1 numerical features
    against Candidate v2 contextual features.

    Final Challenge v2 is not used here.
    """

    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    original = (
        evaluate_numerical_generalization(
            training_dataframe=training,
            challenge_dataframe=development,
        )
    )

    contextual = (
        evaluate_context_generalization(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    context_model = fit_context_model(
        training
    )

    coefficients = (
        get_context_coefficients(
            context_model
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Feature Benchmark"
    )
    print(
        "=" * 62
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
        "Development:"
    )

    print(
        "Challenge Dataset v1 "
        f"({len(development)} samples)"
    )

    print()
    print(
        "FINAL CHALLENGE v2 IS NOT "
        "USED IN THIS EXPERIMENT."
    )

    print_result(
        original
    )

    print_result(
        contextual
    )

    print()
    print("Comparison")
    print("=" * 62)

    print(
        f"{'Metric':<20}"
        f"{'Original':>16}"
        f"{'Context v2':>16}"
    )

    print("-" * 52)

    print(
        f"{'Accuracy':<20}"
        f"{original.accuracy:>16.4f}"
        f"{contextual.accuracy:>16.4f}"
    )

    print(
        f"{'Precision':<20}"
        f"{original.precision:>16.4f}"
        f"{contextual.precision:>16.4f}"
    )

    print(
        f"{'Recall':<20}"
        f"{original.recall:>16.4f}"
        f"{contextual.recall:>16.4f}"
    )

    print(
        f"{'F1':<20}"
        f"{original.f1:>16.4f}"
        f"{contextual.f1:>16.4f}"
    )

    print(
        f"{'ROC AUC':<20}"
        f"{original.roc_auc:>16.4f}"
        f"{contextual.roc_auc:>16.4f}"
    )

    print(
        f"{'False Positives':<20}"
        f"{original.false_positives:>16}"
        f"{contextual.false_positives:>16}"
    )

    print(
        f"{'False Negatives':<20}"
        f"{original.false_negatives:>16}"
        f"{contextual.false_negatives:>16}"
    )

    print()
    print(
        "Context Model Coefficients"
    )
    print("-" * 62)

    print(
        coefficients.to_string(
            index=False
        )
    )

    print()


if __name__ == "__main__":
    main()
