from leakguard.ml.candidate_v2_devset import (
    generate_candidate_v2_devset,
)
from leakguard.ml.dataset_separation import (
    compare_dataset_separation,
    passes_strict_separation,
    sha256_file,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


def create_datasets():
    training = (
        generate_synthetic_dataset_v3(
            samples_per_class=300,
            seed=1337,
        )
    )

    development = (
        generate_candidate_v2_devset(
            samples_per_class=300,
            seed=260815,
        )
    )

    return training, development


def test_candidate_v2_train_dev_sources_are_separate():
    training, development = (
        create_datasets()
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        report[
            "shared_sources"
        ]
        == []
    )


def test_candidate_v2_train_dev_sample_types_are_separate():
    training, development = (
        create_datasets()
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        report[
            "shared_sample_types"
        ]
        == []
    )


def test_candidate_v2_train_dev_has_no_candidate_overlap():
    training, development = (
        create_datasets()
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        report[
            "shared_candidate_pairs"
        ]
        == 0
    )


def test_candidate_v2_train_dev_has_no_exact_value_overlap():
    training, development = (
        create_datasets()
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        report[
            "shared_exact_values"
        ]
        == 0
    )


def test_candidate_v2_strict_separation_passes():
    training, development = (
        create_datasets()
    )

    report = (
        compare_dataset_separation(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert (
        passes_strict_separation(
            report
        )
        is True
    )


def test_sha256_file_is_stable(
    tmp_path,
):
    path = (
        tmp_path
        / "sample.txt"
    )

    path.write_text(
        "LeakGuard Candidate v2",
        encoding="utf-8",
    )

    first = sha256_file(
        path
    )

    second = sha256_file(
        path
    )

    assert first == second
    assert len(first) == 64
