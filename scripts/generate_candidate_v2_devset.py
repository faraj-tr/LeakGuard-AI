from pathlib import Path

from leakguard.ml.candidate_v2_devset import (
    DEFAULT_SAMPLES_PER_CLASS,
    DEVSET_SEED,
    save_candidate_v2_devset,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_candidate_v2_dev_v1.csv"
)


def main():
    dataframe = (
        save_candidate_v2_devset(
            output_path=OUTPUT_PATH,
            samples_per_class=(
                DEFAULT_SAMPLES_PER_CLASS
            ),
            seed=DEVSET_SEED,
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Fresh Development Set"
    )
    print("=" * 58)

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print(
        f"Total samples: "
        f"{len(dataframe)}"
    )

    print(
        "Secret samples: "
        f"{int((dataframe['label'] == 1).sum())}"
    )

    print(
        "Safe samples: "
        f"{int((dataframe['label'] == 0).sum())}"
    )

    print(
        f"Seed: {DEVSET_SEED}"
    )

    print()


if __name__ == "__main__":
    main()
