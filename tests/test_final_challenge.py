import pandas as pd
import pytest

from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.final_challenge import (
    NEGATIVE_TYPES,
    POSITIVE_TYPES,
    generate_final_challenge_dataset,
    save_final_challenge_dataset,
)


def test_final_challenge_is_balanced():
    dataframe = (
        generate_final_challenge_dataset(
            samples_per_class=100,
            seed=8142026,
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


def test_final_challenge_has_required_columns():
    dataframe = (
        generate_final_challenge_dataset(
            samples_per_class=20,
            seed=8142026,
        )
    )

    required = {
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

    assert required.issubset(
        dataframe.columns
    )


def test_final_challenge_is_reproducible():
    first = (
        generate_final_challenge_dataset(
            samples_per_class=50,
            seed=8142026,
        )
    )

    second = (
        generate_final_challenge_dataset(
            samples_per_class=50,
            seed=8142026,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_final_challenge_contains_hard_examples():
    dataframe = (
        generate_final_challenge_dataset(
            samples_per_class=300,
            seed=8142026,
        )
    )

    secrets = dataframe[
        dataframe["label"] == 1
    ]

    safe = dataframe[
        dataframe["label"] == 0
    ]

    neutral_secrets = int(
        (
            secrets[
                "has_sensitive_name"
            ]
            == 0
        ).sum()
    )

    sensitive_safe = int(
        (
            safe[
                "has_sensitive_name"
            ]
            == 1
        ).sum()
    )

    assert neutral_secrets > 0
    assert sensitive_safe > 0


def test_final_challenge_has_high_entropy_safe_values():
    dataframe = (
        generate_final_challenge_dataset(
            samples_per_class=300,
            seed=8142026,
        )
    )

    safe = dataframe[
        dataframe["label"] == 0
    ]

    assert (
        safe["entropy"]
        >= 3.5
    ).any()


def test_final_sample_types_are_new():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    challenge_v1 = (
        generate_challenge_dataset(
            samples_per_class=100,
            seed=2026,
        )
    )

    previous_types = set(
        training["sample_type"]
    ) | set(
        challenge_v1["sample_type"]
    )

    final_types = set(
        POSITIVE_TYPES
    ) | set(
        NEGATIVE_TYPES
    )

    assert final_types.isdisjoint(
        previous_types
    )


def test_final_candidates_do_not_overlap_previous_sets():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=500,
            seed=42,
        )
    )

    challenge_v1 = (
        generate_challenge_dataset(
            samples_per_class=200,
            seed=2026,
        )
    )

    final = (
        generate_final_challenge_dataset(
            samples_per_class=300,
            seed=8142026,
        )
    )

    previous_candidates = set(
        zip(
            training[
                "variable_name"
            ],
            training[
                "value"
            ],
        )
    )

    previous_candidates.update(
        zip(
            challenge_v1[
                "variable_name"
            ],
            challenge_v1[
                "value"
            ],
        )
    )

    final_candidates = set(
        zip(
            final[
                "variable_name"
            ],
            final[
                "value"
            ],
        )
    )

    assert final_candidates.isdisjoint(
        previous_candidates
    )


def test_final_challenge_can_be_saved(
    tmp_path,
):
    output_path = (
        tmp_path
        / "final_challenge.csv"
    )

    dataframe = (
        save_final_challenge_dataset(
            output_path=output_path,
            samples_per_class=20,
            seed=8142026,
        )
    )

    assert output_path.exists()

    loaded = pd.read_csv(
        output_path
    )

    assert len(loaded) == len(
        dataframe
    )


def test_final_challenge_rejects_invalid_size():
    with pytest.raises(
        ValueError
    ):
        generate_final_challenge_dataset(
            samples_per_class=0,
            seed=8142026,
        )
