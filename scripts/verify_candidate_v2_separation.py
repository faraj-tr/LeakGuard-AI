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


def main():
    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Train/Dev Separation Gate"
    )
    print("=" * 72)

    print()
    print(
        f"Training samples: "
        f"{report['training_samples']}"
    )

    print(
        f"Development samples: "
        f"{report['development_samples']}"
    )

    print()
    print(
        "Exact Leakage Checks"
    )
    print("-" * 72)

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

    print()
    print(
        "Dataset Identity"
    )
    print("-" * 72)

    print(
        "Training sources: "
        f"{report['training_sources']}"
    )

    print(
        "Development sources: "
        f"{report['development_sources']}"
    )

    print(
        "Training SHA-256: "
        f"{sha256_file(TRAINING_PATH)}"
    )

    print(
        "Development SHA-256: "
        f"{sha256_file(DEVELOPMENT_PATH)}"
    )

    print()
    print(
        "Strict separation passed: "
        f"{passes_strict_separation(report)}"
    )

    print()


if __name__ == "__main__":
    main()
