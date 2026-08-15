from pathlib import Path

from leakguard.ml.candidate_v2_holdout_benchmark import (
    build_candidate_v2_holdout_report,
    save_candidate_v2_holdout_report,
)
from leakguard.ml.candidate_v2_holdout_gate import (
    EXPECTED_HOLDOUT_SHA256,
    load_frozen_candidate_v2_holdout_bundle,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
    SELECTION_POLICY,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_DEVELOPMENT_SHA256,
    EXPECTED_TRAINING_SHA256,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v3.csv"
)

DEVELOPMENT_PATH = Path(
    "data/processed/"
    "leakguard_candidate_v2_dev_v1.csv"
)

HOLDOUT_PATH = Path(
    "data/processed/"
    "leakguard_candidate_v2_holdout_v1.csv"
)

REPORT_PATH = Path(
    "reports/"
    "candidate_v2_holdout_benchmark_v1.json"
)


def main():
    if REPORT_PATH.exists():
        raise FileExistsError(
            "Holdout benchmark report already "
            "exists. Refusing to rerun or "
            f"overwrite: {REPORT_PATH}"
        )

    training, _, holdout = (
        load_frozen_candidate_v2_holdout_bundle(
            training_path=TRAINING_PATH,
            development_path=(
                DEVELOPMENT_PATH
            ),
            holdout_path=HOLDOUT_PATH,
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Independent Holdout Benchmark"
    )
    print("=" * 78)

    print()
    print(
        "LOCKED CONFIGURATION"
    )
    print("-" * 78)

    print(
        f"Text weight: "
        f"{LOCKED_TEXT_WEIGHT:.2f}"
    )

    print(
        f"Context weight: "
        f"{LOCKED_CONTEXT_WEIGHT:.2f}"
    )

    print(
        f"Threshold: "
        f"{LOCKED_THRESHOLD:.2f}"
    )

    print(
        f"Selection policy: "
        f"{SELECTION_POLICY}"
    )

    print()
    print(
        "FROZEN DATASET IDENTITY"
    )
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

    print(
        "Holdout SHA-256:"
    )
    print(
        EXPECTED_HOLDOUT_SHA256
    )

    print()
    print(
        "Running locked Candidate v2 "
        "on the independent holdout..."
    )

    report = (
        build_candidate_v2_holdout_report(
            training_dataframe=training,
            holdout_dataframe=holdout,
        )
    )

    save_candidate_v2_holdout_report(
        report=report,
        output_path=REPORT_PATH,
    )

    metrics = report[
        "metrics"
    ]

    print()
    print(
        "INDEPENDENT HOLDOUT RESULT"
    )
    print("-" * 78)

    print(
        f"Accuracy:  "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall:    "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"F1 Score:  "
        f"{metrics['f1']:.4f}"
    )

    print(
        f"ROC AUC:   "
        f"{metrics['roc_auc']:.4f}"
    )

    print()
    print(
        f"TP: "
        f"{metrics['true_positives']}"
    )

    print(
        f"TN: "
        f"{metrics['true_negatives']}"
    )

    print(
        f"FP: "
        f"{metrics['false_positives']}"
    )

    print(
        f"FN: "
        f"{metrics['false_negatives']}"
    )

    print()
    print(
        f"Report saved: {REPORT_PATH}"
    )

    print()
    print(
        "HOLDOUT POLICY:"
    )

    print(
        "Do not retune Candidate v2 using "
        "this holdout result."
    )

    print()


if __name__ == "__main__":
    main()
