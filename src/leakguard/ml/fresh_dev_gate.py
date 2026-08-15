from pathlib import Path

import pandas as pd

from leakguard.ml.dataset_separation import (
    sha256_file,
)


EXPECTED_TRAINING_SHA256 = (
    "e19ed8176cf3c00d2465c62d298375ba"
    "9bf51207656f0b411b09ff04aa991e83"
)

EXPECTED_DEVELOPMENT_SHA256 = (
    "02940249dce60658fd041e7b7a77a10"
    "b439fe79273f2b93cfccbbaf3d0d83bf2"
)


def validate_frozen_dataset(
    path: Path,
    expected_sha256: str,
    expected_samples: int,
    expected_source: str,
    expected_label_counts: dict,
) -> pd.DataFrame:
    """
    Load and verify a frozen Candidate v2
    dataset before model evaluation.

    Any unexpected file change causes the
    experiment to stop.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset does not exist: {path}"
        )

    actual_sha256 = sha256_file(
        path
    )

    if actual_sha256 != expected_sha256:
        raise ValueError(
            "Dataset SHA-256 mismatch for "
            f"{path}. Expected "
            f"{expected_sha256}, got "
            f"{actual_sha256}."
        )

    dataframe = pd.read_csv(
        path
    )

    if len(dataframe) != expected_samples:
        raise ValueError(
            "Unexpected sample count for "
            f"{path}. Expected "
            f"{expected_samples}, got "
            f"{len(dataframe)}."
        )

    if "source" not in dataframe.columns:
        raise ValueError(
            "Dataset is missing source column."
        )

    sources = set(
        dataframe[
            "source"
        ]
        .fillna("")
        .astype(str)
    )

    if sources != {
        expected_source
    }:
        raise ValueError(
            "Unexpected dataset source for "
            f"{path}: {sorted(sources)}"
        )

    if "label" not in dataframe.columns:
        raise ValueError(
            "Dataset is missing label column."
        )

    actual_label_counts = (
        dataframe[
            "label"
        ]
        .value_counts()
        .to_dict()
    )

    if actual_label_counts != (
        expected_label_counts
    ):
        raise ValueError(
            "Unexpected label distribution "
            f"for {path}. Expected "
            f"{expected_label_counts}, got "
            f"{actual_label_counts}."
        )

    return dataframe


def load_frozen_candidate_v2_data(
    training_path: Path,
    development_path: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load the frozen Candidate v2 training
    and development datasets.

    Fresh Dev v1 may be used for development
    and fusion tuning, but never described
    as an independent final benchmark after
    it has been inspected.
    """

    training = validate_frozen_dataset(
        path=training_path,
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

    development = validate_frozen_dataset(
        path=development_path,
        expected_sha256=(
            EXPECTED_DEVELOPMENT_SHA256
        ),
        expected_samples=600,
        expected_source=(
            "candidate_v2_dev_v1"
        ),
        expected_label_counts={
            0: 300,
            1: 300,
        },
    )

    return (
        training,
        development,
    )
