import pandas as pd
import pytest

from leakguard.ml.candidate_v2_devset import (
    generate_candidate_v2_devset,
)
from leakguard.ml.candidate_v2_holdout import (
    generate_candidate_v2_holdout,
    save_candidate_v2_holdout,
)
from leakguard.ml.dataset_separation import (
    compare_dataset_separation,
    passes_strict_separation,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


def test_holdout_is_balanced():
    dataframe = (
        generate_candidate_v2_holdout(
            samples_per_class=160,
            seed=8152601,
        )
    )

    counts = (
        dataframe[
            "label"
        ]
        .value_counts()
        .to_dict()
    )

    assert len(dataframe) == 320
    assert counts[0] == 160
    assert counts[1] == 160


def test_holdout_is_reproducible():
    first = (
        generate_candidate_v2_holdout(
            samples_per_class=120,
            seed=8152601,
        )
    )

    second = (
        generate_candidate_v2_holdout(
            samples_per_class=120,
            seed=8152601,
        )
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_holdout_has_no_duplicate_candidates():
    dataframe = (
        generate_candidate_v2_holdout(
            samples_per_class=400,
            seed=8152601,
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


def test_holdout_contains_all_sample_families():
    dataframe = (
        generate_candidate_v2_holdout(
            samples_per_class=400,
            seed=8152601,
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
    ) == 9

    assert len(
        negative_types
    ) == 10


def test_holdout_structural_features_overlap():
    dataframe = (
        generate_candidate_v2_holdout(
            samples_per_class=400,
            seed=8152601,
        )
    )

    features = (
        "looks_like_uuid",
        "looks_like_fixed_hash",
        "is_hex_only",
        "looks_like_jwt",
        "looks_like_passphrase",
        "has_public_frontend_prefix",
    )

    for feature in features:
        safe = dataframe[
            (
                dataframe["label"] == 0
            )
            & (
                dataframe[
                    feature
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
                    feature
                ]
                == 1
            )
        ]

        assert len(safe) > 0
        assert len(secret) > 0


def test_holdout_safe_hash_metadata_exists_in_both_classes():
    dataframe = (
        generate_candidate_v2_holdout(
            samples_per_class=400,
            seed=8152601,
        )
    )

    safe_matches = dataframe[
        (
            dataframe["label"] == 0
        )
        & (
            dataframe[
                "looks_like_safe_hash_metadata"
            ]
            == 1
        )
    ]

    secret_matches = dataframe[
        (
            dataframe["label"] == 1
        )
        & (
            dataframe[
                "looks_like_safe_hash_metadata"
            ]
            == 1
        )
    ]

    assert len(
        safe_matches
    ) > 0

    assert len(
        secret_matches
    ) > 0


def test_holdout_is_strictly_separate_from_training():
    training = (
        generate_synthetic_dataset_v3(
            samples_per_class=160,
            seed=1337,
        )
    )

    holdout = (
        generate_candidate_v2_holdout(
            samples_per_class=160,
            seed=8152601,
        )
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=holdout,
        )
    )

    assert (
        passes_strict_separation(
            report
        )
        is True
    )


def test_holdout_is_strictly_separate_from_development():
    development = (
        generate_candidate_v2_devset(
            samples_per_class=160,
            seed=260815,
        )
    )

    holdout = (
        generate_candidate_v2_holdout(
            samples_per_class=160,
            seed=8152601,
        )
    )

    report = (
        compare_dataset_separation(
            training_dataframe=development,
            development_dataframe=holdout,
        )
    )

    assert (
        passes_strict_separation(
            report
        )
        is True
    )


def test_holdout_can_be_saved(
    tmp_path,
):
    output_path = (
        tmp_path
        / "candidate_v2_holdout.csv"
    )

    dataframe = (
        save_candidate_v2_holdout(
            output_path=output_path,
            samples_per_class=40,
            seed=8152601,
        )
    )

    assert output_path.exists()

    loaded = pd.read_csv(
        output_path
    )

    assert len(loaded) == len(
        dataframe
    )


def test_holdout_rejects_invalid_size():
    with pytest.raises(
        ValueError
    ):
        generate_candidate_v2_holdout(
            samples_per_class=0,
            seed=8152601,
        )

