from pathlib import Path

from leakguard.ml.final_challenge import (
    FINAL_CHALLENGE_SEED,
    FINAL_SAMPLES_PER_CLASS,
    save_final_challenge_dataset,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_final_challenge_v2.csv"
)


def main():
    """
    Generate the untouched final
    generalization dataset.
    """

    dataframe = (
        save_final_challenge_dataset(
            output_path=OUTPUT_PATH,
            samples_per_class=(
                FINAL_SAMPLES_PER_CLASS
            ),
            seed=FINAL_CHALLENGE_SEED,
        )
    )

    secret_count = int(
        (
            dataframe["label"]
            == 1
        ).sum()
    )

    safe_count = int(
        (
            dataframe["label"]
            == 0
        ).sum()
    )

    print()
    print(
        "LeakGuard Final Challenge v2"
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
        f"Seed: "
        f"{FINAL_CHALLENGE_SEED}"
    )

    print()
    print(
        "STATUS: FINAL EVALUATION DATASET"
    )

    print(
        "Do not use this dataset "
        "for training or tuning."
    )

    print()


if __name__ == "__main__":
    main()