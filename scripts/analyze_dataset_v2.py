from pathlib import Path

import pandas as pd

from leakguard.ml.eda import (
    get_feature_summary,
    get_hard_example_counts,
    get_sample_type_distribution,
    get_sensitive_name_analysis,
    summarize_dataset,
    validate_dataset,
)


DATASET_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)


def main():
    """
    Run exploratory data analysis on
    LeakGuard Synthetic Dataset v2.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    dataframe = pd.read_csv(
        DATASET_PATH
    )

    validation = validate_dataset(
        dataframe
    )

    summary = summarize_dataset(
        dataframe
    )

    hard_examples = get_hard_example_counts(
        dataframe
    )

    sensitive_analysis = (
        get_sensitive_name_analysis(
            dataframe
        )
    )

    print()
    print("LeakGuard Dataset v2 EDA")
    print("=" * 40)

    print()
    print("Dataset Summary")
    print("-" * 40)

    print(
        f"Total samples: "
        f"{summary['total_samples']}"
    )

    print(
        f"Secret samples: "
        f"{summary['secret_samples']}"
    )

    print(
        f"Non-secret samples: "
        f"{summary['non_secret_samples']}"
    )

    print(
        f"Secret ratio: "
        f"{summary['secret_ratio']:.2%}"
    )

    print()
    print("Validation")
    print("-" * 40)

    print(
        f"Missing columns: "
        f"{validation['missing_columns']}"
    )

    print(
        f"Valid labels: "
        f"{validation['valid_labels']}"
    )

    print(
        f"Missing values: "
        f"{validation['missing_values']}"
    )

    print(
        f"Duplicate sample IDs: "
        f"{validation['duplicate_sample_ids']}"
    )

    print(
        f"Duplicate full rows: "
        f"{validation['duplicate_rows']}"
    )

    print()
    print("Hard Examples")
    print("-" * 40)

    print(
        "Secrets without sensitive names: "
        f"{hard_examples['positive_without_sensitive_name']}"
    )

    print(
        "Safe samples with sensitive names: "
        f"{hard_examples['negative_with_sensitive_name']}"
    )

    print()
    print("Sensitive Name Analysis")
    print("-" * 40)

    print(
        "Sensitive-name samples: "
        f"{sensitive_analysis['sensitive_name_samples']}"
    )

    print(
        "Secret rate when name is sensitive: "
        f"{sensitive_analysis['sensitive_name_secret_rate']:.2%}"
    )

    print(
        "Non-sensitive-name samples: "
        f"{sensitive_analysis['non_sensitive_name_samples']}"
    )

    print(
        "Secret rate when name is not sensitive: "
        f"{sensitive_analysis['non_sensitive_name_secret_rate']:.2%}"
    )

    print()
    print("Average Features by Label")
    print("-" * 40)

    print(
        get_feature_summary(
            dataframe
        ).to_string()
    )

    print()
    print("Sample Type Distribution")
    print("-" * 40)

    print(
        get_sample_type_distribution(
            dataframe
        ).to_string(
            index=False
        )
    )

    print()


if __name__ == "__main__":
    main()
