from pathlib import Path

import pandas as pd

from leakguard.ml.context_baseline import (
    evaluate_context_generalization,
    fit_context_model,
    get_context_coefficients,
)
from leakguard.ml.context_diagnostics import (
    build_context_predictions,
    get_context_false_negatives,
    get_context_false_positives,
    get_error_type_distribution,
)


TRAINING_V2_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

TRAINING_V3_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v3.csv"
)

DEVELOPMENT_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def print_result(
    title,
    result,
):
    print()
    print(title)
    print("-" * 68)

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
    training_v2 = pd.read_csv(
        TRAINING_V2_PATH
    )

    training_v3 = pd.read_csv(
        TRAINING_V3_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    old_result = (
        evaluate_context_generalization(
            training_dataframe=training_v2,
            development_dataframe=development,
        )
    )

    candidate_v2 = (
        evaluate_context_generalization(
            training_dataframe=training_v3,
            development_dataframe=development,
        )
    )

    predictions = (
        build_context_predictions(
            training_dataframe=training_v3,
            development_dataframe=development,
        )
    )

    false_negatives = (
        get_context_false_negatives(
            predictions
        )
    )

    false_positives = (
        get_context_false_positives(
            predictions
        )
    )

    model = fit_context_model(
        training_v3
    )

    coefficients = (
        get_context_coefficients(
            model
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Development Benchmark"
    )
    print(
        "=" * 68
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Challenge v1 is DEVELOPMENT DATA."
    )

    print(
        "This is a regression experiment, "
        "not an independent final benchmark."
    )

    print(
        "Final Challenge v2 is NOT used."
    )

    print_result(
        (
            "Context Model trained on "
            "Synthetic Dataset v2"
        ),
        old_result,
    )

    print_result(
        (
            "Candidate v2 trained on "
            "Synthetic Dataset v3"
        ),
        candidate_v2,
    )

    print()
    print("Comparison")
    print("=" * 68)

    print(
        f"{'Metric':<20}"
        f"{'Train v2':>16}"
        f"{'Train v3':>16}"
    )

    print("-" * 52)

    print(
        f"{'Accuracy':<20}"
        f"{old_result.accuracy:>16.4f}"
        f"{candidate_v2.accuracy:>16.4f}"
    )

    print(
        f"{'Precision':<20}"
        f"{old_result.precision:>16.4f}"
        f"{candidate_v2.precision:>16.4f}"
    )

    print(
        f"{'Recall':<20}"
        f"{old_result.recall:>16.4f}"
        f"{candidate_v2.recall:>16.4f}"
    )

    print(
        f"{'F1':<20}"
        f"{old_result.f1:>16.4f}"
        f"{candidate_v2.f1:>16.4f}"
    )

    print(
        f"{'ROC AUC':<20}"
        f"{old_result.roc_auc:>16.4f}"
        f"{candidate_v2.roc_auc:>16.4f}"
    )

    print(
        f"{'False Positives':<20}"
        f"{old_result.false_positives:>16}"
        f"{candidate_v2.false_positives:>16}"
    )

    print(
        f"{'False Negatives':<20}"
        f"{old_result.false_negatives:>16}"
        f"{candidate_v2.false_negatives:>16}"
    )

    print()
    print(
        "Candidate v2 False Negative Types"
    )
    print("-" * 68)

    if false_negatives.empty:
        print("None")
    else:
        print(
            get_error_type_distribution(
                false_negatives
            ).to_string(
                index=False
            )
        )

    print()
    print(
        "Candidate v2 False Positive Types"
    )
    print("-" * 68)

    if false_positives.empty:
        print("None")
    else:
        print(
            get_error_type_distribution(
                false_positives
            ).to_string(
                index=False
            )
        )

    print()
    print(
        "Candidate v2 Feature Coefficients"
    )
    print("-" * 68)

    print(
        coefficients.to_string(
            index=False
        )
    )

    print()


if __name__ == "__main__":
    main()
