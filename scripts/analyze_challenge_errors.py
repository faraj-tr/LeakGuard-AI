from pathlib import Path

import pandas as pd

from leakguard.ml.challenge_analysis import (
    build_challenge_predictions,
    get_agreement_summary,
    get_model_errors,
    get_numerical_fixed_text_safe_samples,
    get_text_fixed_numerical_secrets,
    get_type_distribution,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)

CHALLENGE_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def print_distribution(
    title: str,
    dataframe: pd.DataFrame,
):
    """
    Print an error distribution table.
    """

    print()
    print(title)
    print("-" * 56)

    distribution = (
        get_type_distribution(
            dataframe
        )
    )

    if distribution.empty:
        print("None")
        return

    print(
        distribution.to_string(
            index=False
        )
    )


def main():
    """
    Compare numerical and TF-IDF mistakes
    on Challenge Dataset v1.
    """

    training = pd.read_csv(
        TRAINING_PATH
    )

    challenge = pd.read_csv(
        CHALLENGE_PATH
    )

    results = (
        build_challenge_predictions(
            training_dataframe=training,
            challenge_dataframe=challenge,
        )
    )

    numerical_fp = get_model_errors(
        results=results,
        prediction_column=(
            "numerical_prediction"
        ),
        error_type="false_positive",
    )

    numerical_fn = get_model_errors(
        results=results,
        prediction_column=(
            "numerical_prediction"
        ),
        error_type="false_negative",
    )

    text_fp = get_model_errors(
        results=results,
        prediction_column=(
            "text_prediction"
        ),
        error_type="false_positive",
    )

    text_fn = get_model_errors(
        results=results,
        prediction_column=(
            "text_prediction"
        ),
        error_type="false_negative",
    )

    agreement = (
        get_agreement_summary(
            results
        )
    )

    text_fixes = (
        get_text_fixed_numerical_secrets(
            results
        )
    )

    numerical_fixes = (
        get_numerical_fixed_text_safe_samples(
            results
        )
    )

    print()
    print(
        "LeakGuard Challenge Error Analysis"
    )
    print(
        "=" * 56
    )

    print()
    print(
        "Model Error Counts"
    )
    print(
        "-" * 56
    )

    print(
        "Numerical false positives: "
        f"{len(numerical_fp)}"
    )

    print(
        "Numerical false negatives: "
        f"{len(numerical_fn)}"
    )

    print(
        "TF-IDF false positives: "
        f"{len(text_fp)}"
    )

    print(
        "TF-IDF false negatives: "
        f"{len(text_fn)}"
    )

    print()
    print(
        "Model Agreement"
    )
    print(
        "-" * 56
    )

    print(
        "Both correct: "
        f"{agreement['both_correct']}"
    )

    print(
        "Both wrong: "
        f"{agreement['both_wrong']}"
    )

    print(
        "Numerical only correct: "
        f"{agreement['numerical_only_correct']}"
    )

    print(
        "TF-IDF only correct: "
        f"{agreement['text_only_correct']}"
    )

    print_distribution(
        "Numerical False Positive Types",
        numerical_fp,
    )

    print_distribution(
        "Numerical False Negative Types",
        numerical_fn,
    )

    print_distribution(
        "TF-IDF False Positive Types",
        text_fp,
    )

    print_distribution(
        "TF-IDF False Negative Types",
        text_fn,
    )

    print_distribution(
        (
            "Secrets TF-IDF Detects "
            "but Numerical Misses"
        ),
        text_fixes,
    )

    print_distribution(
        (
            "Safe Samples Numerical Handles "
            "but TF-IDF Flags"
        ),
        numerical_fixes,
    )

    print()


if __name__ == "__main__":
    main()