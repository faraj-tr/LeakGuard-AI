import hashlib
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "variable_name",
    "value",
    "sample_type",
    "source",
}


def validate_separation_columns(
    dataframe: pd.DataFrame,
) -> None:
    missing = (
        REQUIRED_COLUMNS
        - set(dataframe.columns)
    )

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing)
            )
        )


def build_candidate_pairs(
    dataframe: pd.DataFrame,
) -> set:
    """
    Return exact variable-name/value pairs.
    """

    validate_separation_columns(
        dataframe
    )

    variable_names = (
        dataframe[
            "variable_name"
        ]
        .fillna("")
        .astype(str)
    )

    values = (
        dataframe[
            "value"
        ]
        .fillna("")
        .astype(str)
    )

    return set(
        zip(
            variable_names,
            values,
        )
    )


def get_exact_values(
    dataframe: pd.DataFrame,
) -> set:
    """
    Return exact candidate values.

    Exact value overlap between synthetic
    training and development data can reveal
    accidental leakage even if variable
    names differ.
    """

    validate_separation_columns(
        dataframe
    )

    return set(
        dataframe[
            "value"
        ]
        .fillna("")
        .astype(str)
    )


def compare_dataset_separation(
    training_dataframe: pd.DataFrame,
    development_dataframe: pd.DataFrame,
) -> dict:
    """
    Compare Candidate v2 training and
    development sets for direct leakage.

    sample_type/source are used only for
    dataset auditing, never as ML features.
    """

    validate_separation_columns(
        training_dataframe
    )

    validate_separation_columns(
        development_dataframe
    )

    training_candidates = (
        build_candidate_pairs(
            training_dataframe
        )
    )

    development_candidates = (
        build_candidate_pairs(
            development_dataframe
        )
    )

    shared_candidates = (
        training_candidates
        & development_candidates
    )

    training_values = (
        get_exact_values(
            training_dataframe
        )
    )

    development_values = (
        get_exact_values(
            development_dataframe
        )
    )

    shared_values = (
        training_values
        & development_values
    )

    training_types = set(
        training_dataframe[
            "sample_type"
        ]
        .fillna("")
        .astype(str)
    )

    development_types = set(
        development_dataframe[
            "sample_type"
        ]
        .fillna("")
        .astype(str)
    )

    shared_sample_types = (
        training_types
        & development_types
    )

    training_sources = set(
        training_dataframe[
            "source"
        ]
        .fillna("")
        .astype(str)
    )

    development_sources = set(
        development_dataframe[
            "source"
        ]
        .fillna("")
        .astype(str)
    )

    shared_sources = (
        training_sources
        & development_sources
    )

    return {
        "training_samples": len(
            training_dataframe
        ),
        "development_samples": len(
            development_dataframe
        ),
        "shared_candidate_pairs": len(
            shared_candidates
        ),
        "shared_exact_values": len(
            shared_values
        ),
        "shared_sample_types": sorted(
            shared_sample_types
        ),
        "shared_sources": sorted(
            shared_sources
        ),
        "training_sources": sorted(
            training_sources
        ),
        "development_sources": sorted(
            development_sources
        ),
    }


def passes_strict_separation(
    report: dict,
) -> bool:
    """
    Candidate v2 strict separation gate.

    We require no exact candidate/value
    overlap and separate generator metadata.
    """

    return (
        report[
            "shared_candidate_pairs"
        ]
        == 0
        and report[
            "shared_exact_values"
        ]
        == 0
        and not report[
            "shared_sample_types"
        ]
        and not report[
            "shared_sources"
        ]
    )


def sha256_file(
    path: Path,
) -> str:
    """
    Return SHA-256 for dataset identity.
    """

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()
