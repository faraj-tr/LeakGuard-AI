from pathlib import Path

from leakguard.ml.candidate_v2_holdout import (
    DEFAULT_SAMPLES_PER_CLASS,
    HOLDOUT_SEED,
    save_candidate_v2_holdout,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "leakguard_candidate_v2_holdout_v1.csv"
)


def main():
    dataframe = (
        save_candidate_v2_holdout(
            output_path=OUTPUT_PATH,
            samples_per_class=(
                DEFAULT_SAMPLES_PER_CLASS
            ),
            seed=HOLDOUT_SEED,
        )
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Independent Holdout v1"
    )
    print("=" * 62)

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
        f"Seed: {HOLDOUT_SEED}"
    )

    print()


if __name__ == "__main__":
    main()
