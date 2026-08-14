from pathlib import Path

import pandas as pd

from leakguard.ml.error_analysis import (
    analyze_baseline_errors,
    get_error_type_distribution,
    get_model_coefficients,
)


DATASET_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)


def main():
    """
    Analyze mistakes made by the
    LeakGuard Logistic Regression baseline.
    """

    dataframe = pd.read_csv(
        DATASET_PATH
    )

    analysis = (
        analyze_baseline_errors(
            dataframe=dataframe,
            test_size=0.20,
            random_state=42,
        )
    )

    false_positives = (
        analysis[
            "false_positives"
        ]
    )

    false_negatives = (
        analysis[
            "false_negatives"
        ]
    )

    print()
    print(
        "LeakGuard Baseline Error Analysis"
    )
    print(
        "=" * 50
    )

    print()
    print(
        "Error Counts"
    )
    print(
        "-" * 50
    )

    print(
        "False Positives: "
        f"{len(false_positives)}"
    )

    print(
        "False Negatives: "
        f"{len(false_negatives)}"
    )

    print()
    print(
        "False Positive Types"
    )
    print(
        "-" * 50
    )

    print(
        get_error_type_distribution(
            false_positives
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "False Negative Types"
    )
    print(
        "-" * 50
    )

    print(
        get_error_type_distribution(
            false_negatives
        ).to_string(
            index=False
        )
    )

    print()
    print(
        "Model Feature Coefficients"
    )
    print(
        "-" * 50
    )

    print(
        get_model_coefficients(
            analysis["model"]
        ).to_string(
            index=False
        )
    )

    display_columns = [
        "variable_name",
        "label",
        "predicted_label",
        "sample_type",
        "length",
        "entropy",
        "has_sensitive_name",
        "is_compact",
        "has_character_variety",
        "secret_probability",
    ]

    print()
    print(
        "False Positive Samples"
    )
    print(
        "-" * 50
    )

    if false_positives.empty:
        print(
            "None"
        )

    else:
        print(
            false_positives[
                display_columns
            ]
            .sort_values(
                "secret_probability",
                ascending=False,
            )
            .to_string(
                index=False
            )
        )

    print()
    print(
        "False Negative Samples"
    )
    print(
        "-" * 50
    )

    if false_negatives.empty:
        print(
            "None"
        )

    else:
        print(
            false_negatives[
                display_columns
            ]
            .sort_values(
                "secret_probability",
                ascending=True,
            )
            .to_string(
                index=False
            )
        )

    print()


if __name__ == "__main__":
    main()