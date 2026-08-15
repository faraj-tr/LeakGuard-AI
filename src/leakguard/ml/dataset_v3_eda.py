import pandas as pd

from leakguard.ml.context_baseline import (
    CONTEXT_ONLY_COLUMNS,
)


REQUIRED_COLUMNS = {
    "sample_id",
    "variable_name",
    "value",
    "label",
    "sample_type",
    "source",
    "has_sensitive_name",
    *CONTEXT_ONLY_COLUMNS,
}


def validate_dataset_v3(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Validate structural quality of
    Synthetic Dataset v3.
    """

    missing_columns = (
        REQUIRED_COLUMNS
        - set(dataframe.columns)
    )

    labels = (
        set(
            dataframe["label"].unique()
        )
        if "label" in dataframe.columns
        else set()
    )

    duplicate_sample_ids = (
        int(
            dataframe[
                "sample_id"
            ].duplicated().sum()
        )
        if "sample_id" in dataframe.columns
        else 0
    )

    duplicate_full_rows = int(
        dataframe.duplicated().sum()
    )

    duplicate_candidates = (
        int(
            dataframe.duplicated(
                subset=[
                    "variable_name",
                    "value",
                ]
            ).sum()
        )
        if {
            "variable_name",
            "value",
        }.issubset(
            dataframe.columns
        )
        else 0
    )

    return {
        "missing_columns": sorted(
            missing_columns
        ),
        "valid_labels": (
            labels == {0, 1}
        ),
        "missing_values": int(
            dataframe.isna().sum().sum()
        ),
        "duplicate_sample_ids": (
            duplicate_sample_ids
        ),
        "duplicate_full_rows": (
            duplicate_full_rows
        ),
        "duplicate_candidates": (
            duplicate_candidates
        ),
    }


def summarize_dataset_v3(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Return basic Dataset v3 statistics.
    """

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

    total = len(
        dataframe
    )

    return {
        "total_samples": total,
        "secret_samples": secret_count,
        "safe_samples": safe_count,
        "secret_ratio": (
            secret_count / total
            if total
            else 0.0
        ),
    }


def get_sample_type_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count each sample type per class.
    """

    return (
        dataframe
        .groupby(
            [
                "label",
                "sample_type",
            ]
        )
        .size()
        .reset_index(
            name="count"
        )
        .sort_values(
            [
                "label",
                "sample_type",
            ]
        )
        .reset_index(
            drop=True
        )
    )


def get_context_activation_by_label(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Measure contextual feature activation
    separately for safe and secret classes.
    """

    records = []

    for feature in CONTEXT_ONLY_COLUMNS:

        for label in (
            0,
            1,
        ):

            subset = dataframe[
                dataframe["label"]
                == label
            ]

            activated = int(
                (
                    subset[
                        feature
                    ]
                    == 1
                ).sum()
            )

            total = len(
                subset
            )

            records.append(
                {
                    "feature": feature,
                    "label": label,
                    "activated": activated,
                    "total": total,
                    "activation_rate": (
                        activated / total
                        if total
                        else 0.0
                    ),
                }
            )

    return pd.DataFrame(
        records
    )


def get_context_secret_rates(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Measure how strongly each contextual
    feature predicts the secret label.
    """

    records = []

    for feature in CONTEXT_ONLY_COLUMNS:

        active = dataframe[
            dataframe[
                feature
            ]
            == 1
        ]

        activated = len(
            active
        )

        secret_count = int(
            (
                active["label"]
                == 1
            ).sum()
        )

        records.append(
            {
                "feature": feature,
                "activated": activated,
                "secret_count": (
                    secret_count
                ),
                "safe_count": (
                    activated
                    - secret_count
                ),
                "secret_rate_when_active": (
                    secret_count / activated
                    if activated
                    else 0.0
                ),
            }
        )

    return pd.DataFrame(
        records
    )


def get_sensitive_name_analysis(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Measure label balance for sensitive
    versus neutral variable names.
    """

    records = []

    for flag in (
        0,
        1,
    ):

        subset = dataframe[
            dataframe[
                "has_sensitive_name"
            ]
            == flag
        ]

        total = len(
            subset
        )

        secrets = int(
            (
                subset["label"]
                == 1
            ).sum()
        )

        records.append(
            {
                "has_sensitive_name": flag,
                "samples": total,
                "secret_samples": secrets,
                "safe_samples": (
                    total - secrets
                ),
                "secret_rate": (
                    secrets / total
                    if total
                    else 0.0
                ),
            }
        )

    return pd.DataFrame(
        records
    )


def get_context_overlap_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Show whether important structural
    features appear in both labels.
    """

    important_features = [
        "looks_like_uuid",
        "looks_like_fixed_hash",
        "is_hex_only",
        "looks_like_jwt",
        "looks_like_passphrase",
        "has_public_frontend_prefix",
    ]

    records = []

    for feature in important_features:

        safe_count = int(
            (
                (
                    dataframe["label"]
                    == 0
                )
                & (
                    dataframe[
                        feature
                    ]
                    == 1
                )
            ).sum()
        )

        secret_count = int(
            (
                (
                    dataframe["label"]
                    == 1
                )
                & (
                    dataframe[
                        feature
                    ]
                    == 1
                )
            ).sum()
        )

        records.append(
            {
                "feature": feature,
                "safe_activations": (
                    safe_count
                ),
                "secret_activations": (
                    secret_count
                ),
                "appears_in_both_classes": (
                    safe_count > 0
                    and secret_count > 0
                ),
            }
        )

    return pd.DataFrame(
        records
    )
