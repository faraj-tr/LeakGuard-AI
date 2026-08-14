from pathlib import Path

from leakguard.ml.dataset import (
    DEFAULT_SAMPLES_PER_CLASS,
    DEFAULT_SEED,
    save_synthetic_dataset,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v1.csv"
)


def main():
    """
    Generate LeakGuard Synthetic Dataset v1.
    """

    dataframe = save_synthetic_dataset(
        output_path=OUTPUT_PATH,
        samples_per_class=DEFAULT_SAMPLES_PER_CLASS,
        seed=DEFAULT_SEED,
    )

    positive_count = int(
        (dataframe["label"] == 1).sum()
    )

    negative_count = int(
        (dataframe["label"] == 0).sum()
    )

    print()
    print("LeakGuard Synthetic Dataset v1")
    print("=" * 34)

    print(f"Output: {OUTPUT_PATH}")
    print(f"Total samples: {len(dataframe)}")
    print(f"Secret samples: {positive_count}")
    print(f"Non-secret samples: {negative_count}")
    print(f"Columns: {len(dataframe.columns)}")
    print(f"Seed: {DEFAULT_SEED}")
    print()


if __name__ == "__main__":
    main()
