from pathlib import Path

import pandas as pd

from leakguard.ml.final_benchmark import (
    build_final_report,
    calculate_file_sha256,
    save_final_report,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

FINAL_DATASET_PATH = Path(
    "data/processed/"
    "leakguard_final_challenge_v2.csv"
)

REPORT_PATH = Path(
    "reports/"
    "final_benchmark_v1.json"
)


def main():
    """
    Run LeakGuard's locked final benchmark.

    This script must never tune the model.
    """

    if not TRAINING_PATH.exists():
        raise FileNotFoundError(
            "Training dataset not found: "
            f"{TRAINING_PATH}"
        )

    if not FINAL_DATASET_PATH.exists():
        raise FileNotFoundError(
            "Final dataset not found: "
            f"{FINAL_DATASET_PATH}"
        )

    if REPORT_PATH.exists():
        raise FileExistsError(
            "Final benchmark was already "
            "recorded at: "
            f"{REPORT_PATH}"
        )

    training = pd.read_csv(
        TRAINING_PATH
    )

    final_dataset = pd.read_csv(
        FINAL_DATASET_PATH
    )

    dataset_sha256 = (
        calculate_file_sha256(
            FINAL_DATASET_PATH
        )
    )

    report = build_final_report(
        training_dataframe=training,
        final_dataframe=final_dataset,
        dataset_sha256=dataset_sha256,
    )

    save_final_report(
        report=report,
        output_path=REPORT_PATH,
    )

    metrics = report["metrics"]

    configuration = report[
        "locked_configuration"
    ]

    print()
    print(
        "LeakGuard FINAL Generalization Benchmark"
    )
    print(
        "=" * 64
    )

    print()
    print(
        "MODEL CONFIGURATION - LOCKED"
    )
    print(
        "-" * 64
    )

    print(
        f"Model: {report['model']}"
    )

    print(
        "Text weight: "
        f"{configuration['text_weight']:.2f}"
    )

    print(
        "Numerical weight: "
        f"{configuration['numerical_weight']:.2f}"
    )

    print(
        "Threshold: "
        f"{configuration['threshold']:.2f}"
    )

    print()
    print("DATASETS")
    print("-" * 64)

    print(
        "Training: "
        f"{report['training_dataset']} "
        f"({report['training_samples']} samples)"
    )

    print(
        "Final evaluation: "
        f"{report['evaluation_dataset']} "
        f"({report['evaluation_samples']} samples)"
    )

    print()
    print("Dataset SHA-256:")

    print(
        report[
            "evaluation_dataset_sha256"
        ]
    )

    print()
    print("FINAL RESULTS")
    print("-" * 64)

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
    print("Confusion Matrix")
    print("-" * 64)

    print(
        f"True Positives:  "
        f"{metrics['true_positives']}"
    )

    print(
        f"True Negatives:  "
        f"{metrics['true_negatives']}"
    )

    print(
        f"False Positives: "
        f"{metrics['false_positives']}"
    )

    print(
        f"False Negatives: "
        f"{metrics['false_negatives']}"
    )

    print()
    print(
        "FINAL BENCHMARK RECORDED"
    )

    print(
        f"Report: {REPORT_PATH}"
    )

    print()
    print(
        "Do NOT tune weights, threshold, "
        "features, or training data using "
        "this result."
    )

    print()


if __name__ == "__main__":
    main()
