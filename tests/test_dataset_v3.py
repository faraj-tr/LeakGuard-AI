import pandas as pd
import pytest

from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
    save_synthetic_dataset_v3,
)


def test_dataset_v3_is_balanced():
    dataframe = (
        generate_synthetic_dataset_v3(
            samples_per_class=100,
            seed=1337,
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


def test_dataset_v3_contains_passphrase_secrets():
    dataframe = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    matches = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "sample_type"
            ]
            == "passphrase_secret"
        )
    ]

    assert len(matches) > 0

    assert (
        matches[
            "looks_like_passphrase"
        ]
        == 1
    ).any()


def test_dataset_v3_contains_jwt_in_both_classes():
    dataframe = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    positives = dataframe[
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

    negatives = dataframe[
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

    assert len(positives) > 0
    assert len(negatives) > 0


def test_dataset_v3_contains_hex_in_both_classes():
    dataframe = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    positives = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "is_hex_only"
            ]
            == 1
        )
    ]

    negatives = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "is_hex_only"
            ]
            == 1
        )
    ]

    assert len(positives) > 0
    assert len(negatives) > 0


def test_dataset_v3_contains_uuid_in_both_classes():
    dataframe = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    positives = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "looks_like_uuid"
            ]
            == 1
        )
    ]

    negatives = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "looks_like_uuid"
            ]
            == 1
        )
    ]

    assert len(positives) > 0
    assert len(negatives) > 0


def test_dataset_v3_has_references_and_placeholders():
    dataframe = (
        generate_synthetic_dataset_v3(
            samples_per_class=200,
            seed=1337,
        )
    )

    assert (
        dataframe[
            "looks_like_reference"
        ]
        == 1
    ).any()

    assert (
        dataframe[
            "looks_like_placeholder"
        ]
        == 1
    ).any()


def test_dataset_v3_is_reproducible():
    first = (
        generate_synthetic_dataset_v3(
            samples_per_class=50,
            seed=1337,
        )
    )

    second = (
        generate_synthetic_dataset_v3(
            samples_per_class=50,
            seed=1337,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_dataset_v3_can_be_saved(
    tmp_path,
):
    output_path = (
        tmp_path
        / "dataset_v3.csv"
    )

    dataframe = (
        save_synthetic_dataset_v3(
            output_path=output_path,
            samples_per_class=20,
            seed=1337,
        )
    )

    assert output_path.exists()

    loaded = pd.read_csv(
        output_path
    )

    assert len(loaded) == len(
        dataframe
    )


def test_dataset_v3_rejects_invalid_size():
    with pytest.raises(
        ValueError
    ):
        generate_synthetic_dataset_v3(
            samples_per_class=0,
            seed=1337,
        )
