import pandas as pd
import pytest

from leakguard.ml.challenge import (
    generate_challenge_dataset,
    save_challenge_dataset,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)


def test_challenge_dataset_is_balanced():
    dataframe = (
        generate_challenge_dataset(
            samples_per_class=100,
            seed=2026,
        )
    )

    counts = (
        dataframe[
            "label"
        ]
        .value_counts()
        .to_dict()
    )

    assert len(dataframe) == 200
    assert counts[0] == 100
    assert counts[1] == 100


def test_challenge_has_required_columns():
    dataframe = (
        generate_challenge_dataset(
            samples_per_class=20,
            seed=2026,
        )
    )

    required_columns = {
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

    assert required_columns.issubset(
        set(
            dataframe.columns
        )
    )


def test_challenge_generation_is_reproducible():
    first = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    second = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_challenge_contains_hard_examples():
    dataframe = (
        generate_challenge_dataset(
            samples_per_class=200,
            seed=2026,
        )
    )

    positives = dataframe[
        dataframe["label"] == 1
    ]

    negatives = dataframe[
        dataframe["label"] == 0
    ]

    neutral_secrets = (
        positives[
            "has_sensitive_name"
        ]
        == 0
    ).sum()

    sensitive_safe = (
        negatives[
            "has_sensitive_name"
        ]
        == 1
    ).sum()

    assert neutral_secrets > 0
    assert sensitive_safe > 0


def test_challenge_has_high_entropy_safe_values():
    dataframe = (
        generate_challenge_dataset(
            samples_per_class=200,
            seed=2026,
        )
    )

    safe_samples = dataframe[
        dataframe["label"] == 0
    ]

    assert (
        safe_samples[
            "entropy"
        ]
        >= 3.5
    ).any()


def test_challenge_has_no_exact_candidate_overlap_with_v2():
    challenge = (
        generate_challenge_dataset(
            samples_per_class=200,
            seed=2026,
        )
    )

    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=500,
            seed=42,
        )
    )

    challenge_candidates = set(
        zip(
            challenge[
                "variable_name"
            ],
            challenge[
                "value"
            ],
        )
    )

    training_candidates = set(
        zip(
            training[
                "variable_name"
            ],
            training[
                "value"
            ],
        )
    )

    assert (
        challenge_candidates
        .isdisjoint(
            training_candidates
        )
    )


def test_challenge_can_be_saved(
    tmp_path,
):
    output_path = (
        tmp_path
        / "challenge.csv"
    )

    dataframe = (
        save_challenge_dataset(
            output_path=output_path,
            samples_per_class=20,
            seed=2026,
        )
    )

    assert output_path.exists()

    loaded = pd.read_csv(
        output_path
    )

    assert len(loaded) == len(
        dataframe
    )


def test_challenge_rejects_invalid_size():
    with pytest.raises(
        ValueError
    ):
        generate_challenge_dataset(
            samples_per_class=0,
            seed=2026,
        )