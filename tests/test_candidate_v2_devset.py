import pandas as pd
import pytest

from leakguard.ml.candidate_v2_devset import (
    generate_candidate_v2_devset,
    save_candidate_v2_devset,
)


def test_candidate_v2_devset_is_balanced():
    dataframe = (
        generate_candidate_v2_devset(
            samples_per_class=120,
            seed=260815,
        )
    )

    counts = (
        dataframe[
            "label"
        ]
        .value_counts()
        .to_dict()
    )

    assert len(dataframe) == 240
    assert counts[0] == 120
    assert counts[1] == 120


def test_candidate_v2_devset_is_reproducible():
    first = (
        generate_candidate_v2_devset(
            samples_per_class=100,
            seed=260815,
        )
    )

    second = (
        generate_candidate_v2_devset(
            samples_per_class=100,
            seed=260815,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_candidate_v2_devset_has_no_duplicate_candidates():
    dataframe = (
        generate_candidate_v2_devset(
            samples_per_class=300,
            seed=260815,
        )
    )

    duplicates = int(
        dataframe.duplicated(
            subset=[
                "variable_name",
                "value",
            ]
        ).sum()
    )

    assert duplicates == 0


def test_candidate_v2_devset_contains_all_sample_families():
    dataframe = (
        generate_candidate_v2_devset(
            samples_per_class=300,
            seed=260815,
        )
    )

    positive_types = set(
        dataframe.loc[
            dataframe["label"] == 1,
            "sample_type",
        ]
    )

    negative_types = set(
        dataframe.loc[
            dataframe["label"] == 0,
            "sample_type",
        ]
    )

    assert len(
        positive_types
    ) == 7

    assert len(
        negative_types
    ) == 9


def test_candidate_v2_devset_identifier_context_exists_in_both_classes():
    dataframe = (
        generate_candidate_v2_devset(
            samples_per_class=300,
            seed=260815,
        )
    )

    safe = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "has_identifier_name"
            ]
            == 1
        )
    ]

    secret = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "has_identifier_name"
            ]
            == 1
        )
    ]

    assert len(safe) > 0
    assert len(secret) > 0


def test_candidate_v2_devset_jwt_exists_in_both_classes():
    dataframe = (
        generate_candidate_v2_devset(
            samples_per_class=300,
            seed=260815,
        )
    )

    safe = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "looks_like_jwt"
            ]
            == 1
        )
    ]

    secret = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "looks_like_jwt"
            ]
            == 1
        )
    ]

    assert len(safe) > 0
    assert len(secret) > 0


def test_candidate_v2_devset_frontend_prefix_exists_in_both_classes():
    dataframe = (
        generate_candidate_v2_devset(
            samples_per_class=300,
            seed=260815,
        )
    )

    safe = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "has_public_frontend_prefix"
            ]
            == 1
        )
    ]

    secret = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "has_public_frontend_prefix"
            ]
            == 1
        )
    ]

    assert len(safe) > 0
    assert len(secret) > 0


def test_candidate_v2_devset_can_be_saved(
    tmp_path,
):
    output_path = (
        tmp_path
        / "candidate_v2_dev.csv"
    )

    dataframe = (
        save_candidate_v2_devset(
            output_path=output_path,
            samples_per_class=40,
            seed=260815,
        )
    )

    assert output_path.exists()

    loaded = pd.read_csv(
        output_path
    )

    assert len(loaded) == len(
        dataframe
    )


def test_candidate_v2_devset_rejects_invalid_size():
    with pytest.raises(
        ValueError
    ):
        generate_candidate_v2_devset(
            samples_per_class=0,
            seed=260815,
        )
