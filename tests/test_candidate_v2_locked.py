from leakguard.ml.candidate_v2_devset import (
    generate_candidate_v2_devset,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
    MINIMUM_DEVELOPMENT_RECALL,
    SELECTION_POLICY,
    build_locked_candidate_v2_decisions,
    evaluate_locked_candidate_v2,
    validate_locked_configuration,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


def create_data():
    training = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    evaluation = (
        generate_candidate_v2_devset(
            samples_per_class=90,
            seed=260815,
        )
    )

    return training, evaluation


def test_locked_candidate_v2_parameters():
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


def test_locked_weights_sum_to_one():
    assert (
        abs(
            (
                LOCKED_TEXT_WEIGHT
                + LOCKED_CONTEXT_WEIGHT
            )
            - 1.0
        )
        < 1e-12
    )


def test_locked_configuration_is_valid():
    validate_locked_configuration()


def test_locked_policy_records_recall_floor():
    assert (
        MINIMUM_DEVELOPMENT_RECALL
        == 0.98
    )

    assert (
        "precision"
        in SELECTION_POLICY.lower()
    )


def test_locked_decisions_match_evaluation_size():
    training, evaluation = (
        create_data()
    )

    decisions = (
        build_locked_candidate_v2_decisions(
            training_dataframe=training,
            evaluation_dataframe=evaluation,
        )
    )

    assert len(
        decisions
    ) == len(
        evaluation
    )

    assert (
        "fusion_probability"
        in decisions.columns
    )

    assert (
        "fusion_prediction"
        in decisions.columns
    )


def test_locked_candidate_v2_metrics_are_valid():
    training, evaluation = (
        create_data()
    )

    result = (
        evaluate_locked_candidate_v2(
            training_dataframe=training,
            evaluation_dataframe=evaluation,
        )
    )

    assert (
        0.0
        <= result.accuracy
        <= 1.0
    )

    assert (
        0.0
        <= result.precision
        <= 1.0
    )

    assert (
        0.0
        <= result.recall
        <= 1.0
    )

    assert (
        0.0
        <= result.f1
        <= 1.0
    )

    assert (
        0.0
        <= result.roc_auc
        <= 1.0
    )
