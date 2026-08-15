from pathlib import Path

from leakguard.ml.candidate_v2_complementarity import (
    get_type_distribution,
)
from leakguard.ml.candidate_v2_fusion import (
    build_candidate_v2_probability_frame,
    build_fusion_decisions,
    get_fusion_false_negatives,
    get_fusion_false_positives,
    search_candidate_v2_fusion,
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


def print_error_types(
    title,
    dataframe,
):
    print()
    print(title)
    print("-" * 78)

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

    probabilities = (
        build_candidate_v2_probability_frame(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    results = (
        search_candidate_v2_fusion(
            probability_frame=probabilities,
            training_samples=len(
                training
            ),
        )
    )

    best = results.iloc[0]

    decisions = (
        build_fusion_decisions(
            probability_frame=probabilities,
            text_weight=float(
                best[
                    "text_weight"
                ]
            ),
            threshold=float(
                best[
                    "threshold"
                ]
            ),
        )
    )

    false_negatives = (
        get_fusion_false_negatives(
            decisions
        )
    )

    false_positives = (
        get_fusion_false_positives(
            decisions
        )
    )

    high_recall = (
        results[
            results[
                "recall"
            ]
            >= 0.95
        ]
        .sort_values(
            by=[
                "precision",
                "f1",
                "false_positives",
            ],
            ascending=[
                False,
                False,
                True,
            ],
        )
        .head(10)
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Late Fusion Development Search"
    )
    print("=" * 78)

    print()
    print(
        "THIS IS DEVELOPMENT TUNING."
    )

    print(
        "Candidate-v2 Dev v1 is no longer "
        "an unseen evaluation set."
    )

    print(
        "No Candidate-v2 holdout has been "
        "used."
    )

    print(
        "Final Challenge v2 is NOT used."
    )

    print()
    print("Frozen Dataset Identity")
    print("-" * 78)

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

    print()
    print(
        "Top Fusion Candidates by F1"
    )
    print("-" * 78)

    columns = [
        "text_weight",
        "context_weight",
        "threshold",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "false_positives",
        "false_negatives",
        "total_errors",
    ]

    print(
        results[
            columns
        ]
        .head(15)
        .to_string(
            index=False
        )
    )

    print()
    print(
        "High-Recall Candidates "
        "(Recall >= 0.95)"
    )
    print("-" * 78)

    if high_recall.empty:
        print("None")
    else:
        print(
            high_recall[
                columns
            ].to_string(
                index=False
            )
        )

    print()
    print(
        "Best Observed Development "
        "Candidate"
    )
    print("-" * 78)

    print(
        f"Text weight: "
        f"{best['text_weight']:.2f}"
    )

    print(
        f"Context weight: "
        f"{best['context_weight']:.2f}"
    )

    print(
        f"Threshold: "
        f"{best['threshold']:.2f}"
    )

    print(
        f"Accuracy: "
        f"{best['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{best['precision']:.4f}"
    )

    print(
        f"Recall: "
        f"{best['recall']:.4f}"
    )

    print(
        f"F1: "
        f"{best['f1']:.4f}"
    )

    print(
        f"ROC AUC: "
        f"{best['roc_auc']:.4f}"
    )

    print(
        f"False Positives: "
        f"{int(best['false_positives'])}"
    )

    print(
        f"False Negatives: "
        f"{int(best['false_negatives'])}"
    )

    print_error_types(
        "Best Candidate False Positives",
        false_positives,
    )

    print_error_types(
        "Best Candidate False Negatives",
        false_negatives,
    )

    print()


if __name__ == "__main__":
    main()
