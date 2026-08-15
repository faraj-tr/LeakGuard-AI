from pathlib import Path

import pandas as pd

from leakguard.ml.context_diagnostics import (
    build_context_predictions,
    compare_feature_activation,
    get_context_false_negatives,
    get_context_false_positives,
    get_error_type_distribution,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

DEVELOPMENT_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def main():
    training = pd.read_csv(
        TRAINING_PATH
    )

    development = pd.read_csv(
        DEVELOPMENT_PATH
    )

    results = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    false_negatives = (
        get_context_false_negatives(
            results
        )
    )

    false_positives = (
        get_context_false_positives(
            results
        )
    )

    activation = (
        compare_feature_activation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Context Diagnostics"
    )
    print(
        "=" * 68
    )

    print()
    print(
        "Development Error Counts"
    )
    print(
        "-" * 68
    )

    print(
        f"False Positives: "
        f"{len(false_positives)}"
    )

    print(
        f"False Negatives: "
        f"{len(false_negatives)}"
    )

    print()
    print(
        "False Negative Types"
    )
    print(
        "-" * 68
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
        "False Positive Types"
    )
    print(
        "-" * 68
    )

    if false_positives.empty:
        print("None")
    else:
        print(
            get_error_type_distribution(
                false_positives
            ).to_string(
                index=False
            )
        )

    print()
    print(
        "Context Feature Activation"
    )
    print(
        "-" * 68
    )

    print(
        activation.to_string(
            index=False
        )
    )

    print()
    print(
        "Lowest-Probability Missed Secrets"
    )
    print(
        "-" * 68
    )

    columns = [
        "variable_name",
        "sample_type",
        "length",
        "entropy",
        "has_sensitive_name",
        "context_probability",
    ]

    if false_negatives.empty:
        print("None")
    else:
        print(
            false_negatives[
                columns
            ]
            .sort_values(
                "context_probability",
                ascending=True,
            )
            .head(20)
            .to_string(
                index=False
            )
        )

    print()


if __name__ == "__main__":
    main()
