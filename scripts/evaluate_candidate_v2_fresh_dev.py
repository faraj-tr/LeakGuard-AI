from pathlib import Path

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
    get_context_false_negatives,
    get_context_false_positives,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_DEVELOPMENT_SHA256,
    EXPECTED_TRAINING_SHA256,
    load_frozen_candidate_v2_data,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v3.csv"
)

DEVELOPMENT_PATH = Path(
    "data/processed/"
    "leakguard_candidate_v2_dev_v1.csv"
)


def print_result(
    result,
):
    print()
    print(result.model_name)
    print("-" * 76)

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


def print_error_types(
    title,
    dataframe,
):
    print()
    print(title)
    print("-" * 76)

    if dataframe.empty:
        print("None")
        return

    print(
        get_type_distribution(
            dataframe
        ).to_string(
            index=False
        )
    )


def main():
    training, development = (
        load_frozen_candidate_v2_data(
            training_path=TRAINING_PATH,
            development_path=(
                DEVELOPMENT_PATH
            ),
        )
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

    context_false_negatives = (
        get_context_false_negatives(
            context_predictions
        )
    )

    context_false_positives = (
        get_context_false_positives(
            context_predictions
        )
    )

    text_false_negatives = (
        text_predictions[
            (
                text_predictions[
                    "label"
                ]
                == 1
            )
            & (
                text_predictions[
                    "text_prediction"
                ]
                == 0
            )
        ]
    )

    text_false_positives = (
        text_predictions[
            (
                text_predictions[
                    "label"
                ]
                == 0
            )
            & (
                text_predictions[
                    "text_prediction"
                ]
                == 1
            )
        ]
    )

    text_only_correct = comparison[
        comparison[
            "outcome"
        ]
        == "text_only_correct"
    ]

    context_only_correct = comparison[
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
        "Frozen Fresh-Dev Baseline"
    )
    print("=" * 76)

    print()
    print(
        "NO FUSION TUNING HAS BEEN "
        "PERFORMED ON THIS DATASET YET."
    )

    print(
        "Final Challenge v2 is NOT used."
    )

    print()
    print("Frozen Dataset Identity")
    print("-" * 76)

    print(
        "Training SHA-256:"
    )

    print(
        EXPECTED_TRAINING_SHA256
    )

    print(
        "Development SHA-256:"
    )

    print(
        EXPECTED_DEVELOPMENT_SHA256
    )

    print_result(
        context_metrics
    )

    print_result(
        text_metrics
    )

    print()
    print("Model Complementarity")
    print("-" * 76)

    print(
        get_outcome_summary(
            comparison
        ).to_string(
            index=False
        )
    )

    print_error_types(
        "Context False Negative Types",
        context_false_negatives,
    )

    print_error_types(
        "Context False Positive Types",
        context_false_positives,
    )

    print_error_types(
        "Text False Negative Types",
        text_false_negatives,
    )

    print_error_types(
        "Text False Positive Types",
        text_false_positives,
    )

    print_error_types(
        "Errors Rescued by Text",
        text_only_correct,
    )

    print_error_types(
        "Errors Rescued by Context",
        context_only_correct,
    )

    print_error_types(
        "Errors Both Models Miss",
        both_wrong,
    )

    print()


if __name__ == "__main__":
    main()
