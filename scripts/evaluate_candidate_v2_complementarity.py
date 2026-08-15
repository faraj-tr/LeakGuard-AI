from pathlib import Path

import pandas as pd

from leakguard.ml.candidate_v2_complementarity import (
    build_complementarity_frame,
    build_text_predictions,
    evaluate_text_probe,
    get_outcome_summary,
    get_type_distribution,
)
from leakguard.ml.context_baseline import (
    evaluate_context_generalization,
)
from leakguard.ml.context_diagnostics import (
    build_context_predictions,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v3.csv"
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
    print("-" * 72)

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
    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    context_metrics = (
        evaluate_context_generalization(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    text_metrics = (
        evaluate_text_probe(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    context_predictions = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    text_predictions = (
        build_text_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    comparison = (
        build_complementarity_frame(
            context_results=(
                context_predictions
            ),
            text_results=(
                text_predictions
            ),
        )
    )

    text_rescues = comparison[
        comparison[
            "outcome"
        ]
        == "text_only_correct"
    ]

    context_rescues = comparison[
        comparison[
            "outcome"
        ]
        == "context_only_correct"
    ]

    both_wrong = comparison[
        comparison[
            "outcome"
        ]
        == "both_wrong"
    ]

    print()
    print(
        "LeakGuard Candidate v2 "
        "Complementarity Study"
    )
    print(
        "=" * 72
    )

    print()
    print(
        "Challenge v1 is DEVELOPMENT DATA."
    )

    print(
        "Final Challenge v2 is NOT used."
    )

    print_result(
        context_metrics
    )

    print_result(
        text_metrics
    )

    print()
    print(
        "Model Complementarity"
    )
    print("-" * 72)

    print(
        get_outcome_summary(
            comparison
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "Errors rescued by Text"
    )
    print("-" * 72)

    if text_rescues.empty:
        print("None")
    else:
        print(
            get_type_distribution(
                text_rescues
            ).to_string(
                index=False
            )
        )

    print()
    print(
        "Errors rescued by Context"
    )
    print("-" * 72)

    if context_rescues.empty:
        print("None")
    else:
        print(
            get_type_distribution(
                context_rescues
            ).to_string(
                index=False
            )
        )

    print()
    print(
        "Errors Both Models Miss"
    )
    print("-" * 72)

    if both_wrong.empty:
        print("None")
    else:
        print(
            get_type_distribution(
                both_wrong
            ).to_string(
                index=False
            )
        )

    print()


if __name__ == "__main__":
    main()
