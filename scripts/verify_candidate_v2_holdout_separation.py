from pathlib import Path

import pandas as pd

from leakguard.ml.dataset_separation import (
    compare_dataset_separation,
    passes_strict_separation,
    sha256_file,
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


def print_report(
    title,
    report,
):
    print()
    print(title)
    print("-" * 78)

    print(
        "Shared candidate pairs: "
        f"{report['shared_candidate_pairs']}"
    )

    print(
        "Shared exact values: "
        f"{report['shared_exact_values']}"
    )

    print(
        "Shared sample types: "
        f"{report['shared_sample_types']}"
    )

    print(
        "Shared sources: "
        f"{report['shared_sources']}"
    )

    print(
        "Strict separation passed: "
        f"{passes_strict_separation(report)}"
    )


def main():
    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    holdout = pd.read_csv(
        HOLDOUT_PATH
    )

    train_holdout = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=holdout,
        )
    )

    dev_holdout = (
        compare_dataset_separation(
            training_dataframe=development,
            development_dataframe=holdout,
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Independent Holdout Separation Gate"
    )
    print("=" * 78)

    print_report(
        "Training v3 vs Holdout v1",
        train_holdout,
    )

    print_report(
        "Development v1 vs Holdout v1",
        dev_holdout,
    )

    print()
    print("Dataset Identity")
    print("-" * 78)

    print(
        "Training SHA-256:"
    )
    print(
        sha256_file(
            TRAINING_PATH
        )
    )

    print(
        "Development SHA-256:"
    )
    print(
        sha256_file(
            DEVELOPMENT_PATH
        )
    )

    print(
        "Holdout SHA-256:"
    )
    print(
        sha256_file(
            HOLDOUT_PATH
        )
    )

    print()

    overall_passed = (
        passes_strict_separation(
            train_holdout
        )
        and passes_strict_separation(
            dev_holdout
        )
    )

    print(
        "OVERALL HOLDOUT SEPARATION "
        f"PASSED: {overall_passed}"
    )

    print()


if __name__ == "__main__":
    main()
