from pathlib import Path

from leakguard.ml.challenge import (
    CHALLENGE_SAMPLES_PER_CLASS,
    CHALLENGE_SEED,
    save_challenge_dataset,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_challenge_v1.csv"
)


def main():
    """
    Generate LeakGuard Challenge Dataset v1.
    """

    dataframe = save_challenge_dataset(
        output_path=OUTPUT_PATH,
        samples_per_class=(
            CHALLENGE_SAMPLES_PER_CLASS
        ),
        seed=CHALLENGE_SEED,
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
        "LeakGuard Challenge Dataset v1"
    )
    print(
        "=" * 44
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
        f"Seed: {CHALLENGE_SEED}"
    )

    print()


if __name__ == "__main__":
    main()