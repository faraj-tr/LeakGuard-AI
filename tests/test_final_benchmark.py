import json

import pytest

from leakguard.ml.dataset_v2 import (
    generate_synthetic_dataset_v2,
)
from leakguard.ml.final_benchmark import (
    build_final_report,
    calculate_file_sha256,
    save_final_report,
    validate_final_dataset,
)
from leakguard.ml.final_challenge import (
    generate_final_challenge_dataset,
)


def create_full_final_dataset():
    return (
        generate_final_challenge_dataset(
            samples_per_class=300,
            seed=8142026,
        )
    )


def test_final_dataset_validation_accepts_expected_set():
    dataframe = (
        create_full_final_dataset()
    )

    validate_final_dataset(
        dataframe
    )


def test_final_dataset_validation_rejects_wrong_size():
    dataframe = (
        generate_final_challenge_dataset(
            samples_per_class=20,
            seed=8142026,
        )
    )

    with pytest.raises(
        ValueError
    ):
        validate_final_dataset(
            dataframe
        )


def test_sha256_is_stable(
    tmp_path,
):
    path = (
        tmp_path
        / "sample.txt"
    )

    path.write_text(
        "LeakGuard",
        encoding="utf-8",
    )

    first = (
        calculate_file_sha256(
            path
        )
    )

    second = (
        calculate_file_sha256(
            path
        )
    )

    assert first == second
    assert len(first) == 64


def test_final_report_contains_locked_policy():
    training = (
        generate_synthetic_dataset_v2(
            samples_per_class=100,
            seed=42,
        )
    )

    final_dataset = (
        create_full_final_dataset()
    )

    report = build_final_report(
        training_dataframe=training,
        final_dataframe=final_dataset,
        dataset_sha256=(
            "a" * 64
        ),
    )

    assert (
        report["status"]
        == "FINAL_EVALUATION"
    )

    assert (
        report["policy"][
            "used_for_training"
        ]
        is False
    )

    assert (
        report["policy"][
            "used_for_tuning"
        ]
        is False
    )

    assert (
        report["policy"][
            "weights_locked_before_test"
        ]
        is True
    )

    assert (
        report["policy"][
            "threshold_locked_before_test"
        ]
        is True
    )


def test_final_report_cannot_be_overwritten(
    tmp_path,
):
    output_path = (
        tmp_path
        / "final.json"
    )

    report = {
        "result": "test",
    }

    save_final_report(
        report=report,
        output_path=output_path,
    )

    with pytest.raises(
        FileExistsError
    ):
        save_final_report(
            report=report,
            output_path=output_path,
        )

    loaded = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert (
        loaded["result"]
        == "test"
    )