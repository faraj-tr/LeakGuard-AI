from pathlib import Path

import pandas as pd

from leakguard.ml.dataset_v3_eda import (
    get_context_activation_by_label,
    get_context_overlap_summary,
    get_context_secret_rates,
    get_sample_type_distribution,
    get_sensitive_name_analysis,
    summarize_dataset_v3,
    validate_dataset_v3,
)


DATASET_PATH = Path(
    "data/processed/"
    "leakguard_candidate_v2_dev_v1.csv"
)


def main():
    dataframe = pd.read_csv(
        DATASET_PATH
    )

    summary = summarize_dataset_v3(
        dataframe
    )

    validation = validate_dataset_v3(
        dataframe
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Development Set Quality Gate"
    )
    print("=" * 76)

    print()
    print("Dataset Summary")
    print("-" * 76)

    print(
        f"Total samples: "
        f"{summary['total_samples']}"
    )

    print(
        f"Secret samples: "
        f"{summary['secret_samples']}"
    )

    print(
        f"Safe samples: "
        f"{summary['safe_samples']}"
    )

    print(
        f"Secret ratio: "
        f"{summary['secret_ratio']:.2%}"
    )

    print()
    print("Validation")
    print("-" * 76)

    for key, value in (
        validation.items()
    ):
        print(
            f"{key}: {value}"
        )

    print()
    print(
        "Sensitive Name Analysis"
    )
    print("-" * 76)

    print(
        get_sensitive_name_analysis(
            dataframe
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "Context Overlap Summary"
    )
    print("-" * 76)

    print(
        get_context_overlap_summary(
            dataframe
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "Context Feature Secret Rates"
    )
    print("-" * 76)

    print(
        get_context_secret_rates(
            dataframe
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "Context Activation by Label"
    )
    print("-" * 76)

    print(
        get_context_activation_by_label(
            dataframe
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "Sample Type Distribution"
    )
    print("-" * 76)

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
