import pandas as pd


REQUIRED_COLUMNS = {
    "sample_id",
    "variable_name",
    "value",
    "label",
    "sample_type",
    "framework",
    "source",
    "length",
    "entropy",
    "digit_ratio",
    "uppercase_ratio",
    "special_ratio",
    "has_sensitive_name",
    "is_compact",
    "has_character_variety",
}


NUMERIC_FEATURE_COLUMNS = [
    "length",
    "entropy",
    "digit_ratio",
    "uppercase_ratio",
    "special_ratio",
    "has_sensitive_name",
    "is_compact",
    "has_character_variety",
]


def validate_dataset(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Validate the basic structure and quality
    of a LeakGuard dataset.
    """

    missing_columns = (
        REQUIRED_COLUMNS
        - set(dataframe.columns)
    )

    labels = set(
        dataframe["label"].unique()
    ) if "label" in dataframe else set()

    missing_values = int(
        dataframe.isnull()
        .sum()
        .sum()
    )

    duplicate_sample_ids = int(
        dataframe["sample_id"]
        .duplicated()
        .sum()
    ) if "sample_id" in dataframe else 0

    duplicate_rows = int(
        dataframe.duplicated()
        .sum()
    )

    return {
        "missing_columns": sorted(
            missing_columns
        ),
        "valid_labels": (
            labels.issubset(
                {0, 1}
            )
        ),
        "missing_values": (
            missing_values
        ),
        "duplicate_sample_ids": (
            duplicate_sample_ids
        ),
        "duplicate_rows": (
            duplicate_rows
        ),
    }


def summarize_dataset(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Return high-level statistics about
    dataset size and class balance.
    """

    total_samples = len(
        dataframe
    )

    secret_samples = int(
        (
            dataframe["label"]
            == 1
        ).sum()
    )

    non_secret_samples = int(
        (
            dataframe["label"]
            == 0
        ).sum()
    )

    secret_ratio = (
        secret_samples
        / total_samples
        if total_samples
        else 0.0
    )

    return {
        "total_samples": (
            total_samples
        ),
        "secret_samples": (
            secret_samples
        ),
        "non_secret_samples": (
            non_secret_samples
        ),
        "secret_ratio": round(
            secret_ratio,
            4,
        ),
    }


def get_feature_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the average numerical feature
    values for each class.

    label:
        0 = non-secret
        1 = secret
    """

    return (
        dataframe
        .groupby("label")[
            NUMERIC_FEATURE_COLUMNS
        ]
        .mean()
        .round(4)
    )


def get_sample_type_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count dataset samples by label and
    synthetic sample type.
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


def get_hard_example_counts(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Measure intentionally difficult samples.

    Positive hard example:
        Real secret-like sample with a
        non-sensitive variable name.

    Negative hard example:
        Safe sample using a sensitive-looking
        variable name.
    """

    secret_samples = dataframe[
        dataframe["label"] == 1
    ]

    non_secret_samples = dataframe[
        dataframe["label"] == 0
    ]

    positive_without_sensitive_name = int(
        (
            secret_samples[
                "has_sensitive_name"
            ]
            == 0
        ).sum()
    )

    negative_with_sensitive_name = int(
        (
            non_secret_samples[
                "has_sensitive_name"
            ]
            == 1
        ).sum()
    )

    return {
        (
            "positive_without_"
            "sensitive_name"
        ): (
            positive_without_sensitive_name
        ),
        (
            "negative_with_"
            "sensitive_name"
        ): (
            negative_with_sensitive_name
        ),
    }


def get_sensitive_name_analysis(
    dataframe: pd.DataFrame,
) -> dict:
    """
    Analyze whether sensitive variable names
    are too strongly correlated with labels.

    This helps detect shortcut-learning risk.
    """

    sensitive = dataframe[
        dataframe[
            "has_sensitive_name"
        ] == 1
    ]

    non_sensitive = dataframe[
        dataframe[
            "has_sensitive_name"
        ] == 0
    ]

    sensitive_secret_rate = (
        float(
            sensitive["label"]
            .mean()
        )
        if len(sensitive)
        else 0.0
    )

    non_sensitive_secret_rate = (
        float(
            non_sensitive["label"]
            .mean()
        )
        if len(non_sensitive)
        else 0.0
    )

    return {
        "sensitive_name_samples": (
            len(sensitive)
        ),
        "sensitive_name_secret_rate": round(
            sensitive_secret_rate,
            4,
        ),
        "non_sensitive_name_samples": (
            len(non_sensitive)
        ),
        (
            "non_sensitive_name_"
            "secret_rate"
        ): round(
            non_sensitive_secret_rate,
            4,
        ),
    }