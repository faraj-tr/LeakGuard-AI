from pathlib import Path

from leakguard.ml.candidate_v2_artifact import (
    save_candidate_v2_artifact,
    build_candidate_v2_artifact_payload,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_TRAINING_SHA256,
    validate_frozen_dataset,
)


TRAINING_PATH = Path(
    "data/processed/"
    "leakguard_synthetic_v3.csv"
)

ARTIFACT_PATH = Path(
    "models/"
    "candidate_v2_advisory_v1.pkl"
)


def main():
    training = validate_frozen_dataset(
        path=TRAINING_PATH,
        expected_sha256=(
            EXPECTED_TRAINING_SHA256
        ),
        expected_samples=2000,
        expected_source="synthetic_v3",
        expected_label_counts={
            0: 1000,
            1: 1000,
        },
    )

    payload = (
        build_candidate_v2_artifact_payload(
            training_dataframe=training,
            training_source=(
                "synthetic_v3"
            ),
            training_sha256=(
                EXPECTED_TRAINING_SHA256
            ),
        )
    )

    artifact_sha256 = (
        save_candidate_v2_artifact(
            payload=payload,
            output_path=(
                ARTIFACT_PATH
            ),
        )
    )

    size_bytes = (
        ARTIFACT_PATH
        .stat()
        .st_size
    )

    print()
    print(
        "LeakGuard Candidate v2 "
        "Advisory Model Artifact"
    )
    print("=" * 72)

    print()
    print("Artifact")
    print("-" * 72)

    print(
        f"Path: {ARTIFACT_PATH}"
    )

    print(
        f"Size: {size_bytes} bytes"
    )

    print(
        "SHA-256:"
    )

    print(
        artifact_sha256
    )

    print()
    print(
        "Frozen Training Identity"
    )
    print("-" * 72)

    print(
        "Source: synthetic_v3"
    )

    print(
        "Training SHA-256:"
    )

    print(
        EXPECTED_TRAINING_SHA256
    )

    print(
        f"Samples: {len(training)}"
    )

    print()
    print(
        "Locked Configuration"
    )
    print("-" * 72)

    print(
        f"Text weight: "
        f"{LOCKED_TEXT_WEIGHT:.2f}"
    )

    print(
        f"Context weight: "
        f"{LOCKED_CONTEXT_WEIGHT:.2f}"
    )

    print(
        f"Threshold: "
        f"{LOCKED_THRESHOLD:.2f}"
    )

    print()
    print(
        "Mode: advisory"
    )

    print(
        "Blocking authority: False"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Freeze the artifact SHA-256 "
        "before enabling runtime loading."
    )

    print(
        "Do not overwrite this artifact."
    )

    print()


if __name__ == "__main__":
    main()
