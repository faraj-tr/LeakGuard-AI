from pathlib import Path

from leakguard.ml.dataset_v2 import (
    V2_DEFAULT_SAMPLES_PER_CLASS,
    V2_DEFAULT_SEED,
    save_synthetic_dataset_v2,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v2.csv"
)


def main():
    """
    Generate LeakGuard Synthetic Dataset v2.
    """

    dataframe = save_synthetic_dataset_v2(
        output_path=OUTPUT_PATH,
        samples_per_class=V2_DEFAULT_SAMPLES_PER_CLASS,
        seed=V2_DEFAULT_SEED,
    )

    secret_count = int(
        (dataframe["label"] == 1).sum()
    )

    non_secret_count = int(
        (dataframe["label"] == 0).sum()
    )

    sensitive_positive_count = int(
        (
            (dataframe["label"] == 1)
            & (dataframe["has_sensitive_name"] == 1)
        ).sum()
    )

    sensitive_negative_count = int(
        (
            (dataframe["label"] == 0)
            & (dataframe["has_sensitive_name"] == 1)
        ).sum()
    )

    print()
    print("LeakGuard Synthetic Dataset v2")
    print("=" * 40)

    print(f"Output: {OUTPUT_PATH}")
    print(f"Total samples: {len(dataframe)}")
    print(f"Secret samples: {secret_count}")
    print(f"Non-secret samples: {non_secret_count}")
    print(
        "Secrets with sensitive names: "
        f"{sensitive_positive_count}"
    )
    print(
        "Safe samples with sensitive names: "
        f"{sensitive_negative_count}"
    )
    print(f"Seed: {V2_DEFAULT_SEED}")
    print()


if __name__ == "__main__":
    main()
