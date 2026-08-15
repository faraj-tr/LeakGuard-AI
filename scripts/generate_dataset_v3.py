from pathlib import Path

from leakguard.ml.dataset_v3 import (
    DATASET_V3_SEED,
    DEFAULT_SAMPLES_PER_CLASS,
    save_synthetic_dataset_v3,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v3.csv"
)


def main():
    dataframe = (
        save_synthetic_dataset_v3(
            output_path=OUTPUT_PATH,
            samples_per_class=(
                DEFAULT_SAMPLES_PER_CLASS
            ),
            seed=DATASET_V3_SEED,
        )
    )

    secret_count = int(
        (
            dataframe["label"] == 1
        ).sum()
    )

    safe_count = int(
        (
            dataframe["label"] == 0
        ).sum()
    )

    print()
    print(
        "LeakGuard Synthetic Dataset v3"
    )
    print(
        "=" * 52
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print(
        f"Total samples: "
        f"{len(dataframe)}"
    )

    print(
        f"Secret samples: "
        f"{secret_count}"
    )

    print(
        f"Safe samples: "
        f"{safe_count}"
    )

    print(
        f"Seed: {DATASET_V3_SEED}"
    )

    print()


if __name__ == "__main__":
    main()
