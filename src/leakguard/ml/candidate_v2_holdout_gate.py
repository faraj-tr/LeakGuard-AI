from pathlib import Path

import pandas as pd

from leakguard.ml.dataset_separation import (
    compare_dataset_separation,
    passes_strict_separation,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_DEVELOPMENT_SHA256,
    EXPECTED_TRAINING_SHA256,
    validate_frozen_dataset,
)


EXPECTED_HOLDOUT_SHA256 = (
    "391d75e8a0fa5bc8776e5f466388c527"
    "d228a4cbef5debd96a5714843ff93bf7"
)


def load_frozen_candidate_v2_holdout_bundle(
    training_path: Path,
    development_path: Path,
    holdout_path: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load and verify every frozen dataset
    required for Candidate v2 independent
    holdout evaluation.

    The holdout must remain separate from
    both training and development data.
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

    holdout = validate_frozen_dataset(
        path=holdout_path,
        expected_sha256=(
            EXPECTED_HOLDOUT_SHA256
        ),
        expected_samples=800,
        expected_source=(
            "candidate_v2_holdout_v1"
        ),
        expected_label_counts={
            0: 400,
            1: 400,
        },
    )

    train_holdout_report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=holdout,
        )
    )

    dev_holdout_report = (
        compare_dataset_separation(
            training_dataframe=development,
            development_dataframe=holdout,
        )
    )

    if not passes_strict_separation(
        train_holdout_report
    ):
        raise ValueError(
            "Candidate v2 holdout failed "
            "strict separation from training."
        )

    if not passes_strict_separation(
        dev_holdout_report
    ):
        raise ValueError(
            "Candidate v2 holdout failed "
            "strict separation from development."
        )

    return (
        training,
        development,
        holdout,
    )
