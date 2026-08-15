import pytest

from leakguard.ml.candidate_v2_holdout import (
    generate_candidate_v2_holdout,
)
from leakguard.ml.candidate_v2_holdout_benchmark import (
    build_candidate_v2_holdout_report,
    save_candidate_v2_holdout_report,
)
from leakguard.ml.candidate_v2_holdout_gate import (
    EXPECTED_HOLDOUT_SHA256,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


def create_data():
    training = (
        generate_synthetic_dataset_v3(
            samples_per_class=180,
            seed=1337,
        )
    )

    holdout = (
        generate_candidate_v2_holdout(
            samples_per_class=180,
            seed=8152601,
        )
    )

    return training, holdout


def test_holdout_hash_constant_is_sha256():
    assert len(
        EXPECTED_HOLDOUT_SHA256
    ) == 64


def test_locked_holdout_configuration_is_expected():
    assert (
        LOCKED_TEXT_WEIGHT
        == 0.70
    )

    assert (
        LOCKED_CONTEXT_WEIGHT
        == 0.30
    )

    assert (
        LOCKED_THRESHOLD
        == 0.50
    )


def test_holdout_report_contains_policy():
    training, holdout = (
        create_data()
    )

    report = (
        build_candidate_v2_holdout_report(
            training_dataframe=training,
            holdout_dataframe=holdout,
        )
    )

    policy = report[
        "evaluation_policy"
    ]

    assert (
        policy[
            "holdout_used_for_training"
        ]
        is False
    )

    assert (
        policy[
            "holdout_used_for_tuning"
        ]
        is False
    )

    assert (
        policy[
            "parameters_locked_before_holdout"
        ]
        is True
    )

    assert (
        policy[
            "do_not_retune_from_holdout"
        ]
        is True
    )


def test_holdout_report_metrics_are_valid():
    training, holdout = (
        create_data()
    )

    report = (
        build_candidate_v2_holdout_report(
            training_dataframe=training,
            holdout_dataframe=holdout,
        )
    )

    metrics = report[
        "metrics"
    ]

    for key in (
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    ):
        assert (
            0.0
            <= metrics[key]
            <= 1.0
        )


def test_holdout_confusion_counts_match_size():
    training, holdout = (
        create_data()
    )

    report = (
        build_candidate_v2_holdout_report(
            training_dataframe=training,
            holdout_dataframe=holdout,
        )
    )

    metrics = report[
        "metrics"
    ]

    total = (
        metrics[
            "true_positives"
        ]
        + metrics[
            "true_negatives"
        ]
        + metrics[
            "false_positives"
        ]
        + metrics[
            "false_negatives"
        ]
    )

    assert total == len(
        holdout
    )


def test_holdout_report_can_be_saved(
    tmp_path,
):
    training, holdout = (
        create_data()
    )

    report = (
        build_candidate_v2_holdout_report(
            training_dataframe=training,
            holdout_dataframe=holdout,
        )
    )

    output_path = (
        tmp_path
        / "benchmark.json"
    )

    save_candidate_v2_holdout_report(
        report=report,
        output_path=output_path,
    )

    assert output_path.exists()


def test_holdout_report_refuses_overwrite(
    tmp_path,
):
    training, holdout = (
        create_data()
    )

    report = (
        build_candidate_v2_holdout_report(
            training_dataframe=training,
            holdout_dataframe=holdout,
        )
    )

    output_path = (
        tmp_path
        / "benchmark.json"
    )

    save_candidate_v2_holdout_report(
        report=report,
        output_path=output_path,
    )

    with pytest.raises(
        FileExistsError
    ):
        save_candidate_v2_holdout_report(
            report=report,
            output_path=output_path,
        )
