from copy import deepcopy

import pytest

from leakguard.ml.candidate_v2_artifact import (
    ARTIFACT_SCHEMA_VERSION,
    ArtifactCompatibilityError,
    ArtifactExistsError,
    ArtifactIntegrityError,
    build_candidate_v2_artifact_payload,
    load_candidate_v2_artifact,
    save_candidate_v2_artifact,
    sha256_file,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


TEST_SECRET = (
    "K7mP2xQ9vL4sN8zA1c"
)


@pytest.fixture(
    scope="module"
)
def training_dataframe():
    return (
        generate_synthetic_dataset_v3(
            samples_per_class=180,
            seed=1337,
        )
    )


@pytest.fixture(
    scope="module"
)
def artifact_payload(
    training_dataframe,
):
    return (
        build_candidate_v2_artifact_payload(
            training_dataframe=(
                training_dataframe
            ),
            training_source=(
                "unit_test_training"
            ),
            training_sha256=(
                "test-training-sha256"
            ),
        )
    )


def test_artifact_payload_has_expected_schema(
    artifact_payload,
):
    assert artifact_payload[
        "schema_version"
    ] == ARTIFACT_SCHEMA_VERSION

    assert artifact_payload[
        "model_name"
    ] == "candidate-v2"

    assert artifact_payload[
        "mode"
    ] == "advisory"

    assert (
        "training_dataframe"
        not in artifact_payload
    )


def test_artifact_can_be_saved_and_hashed(
    tmp_path,
    artifact_payload,
):
    output_path = (
        tmp_path
        / "candidate-v2.pkl"
    )

    artifact_sha256 = (
        save_candidate_v2_artifact(
            payload=artifact_payload,
            output_path=output_path,
        )
    )

    assert output_path.exists()

    assert len(
        artifact_sha256
    ) == 64

    assert artifact_sha256 == (
        sha256_file(
            output_path
        )
    )


def test_artifact_refuses_overwrite(
    tmp_path,
    artifact_payload,
):
    output_path = (
        tmp_path
        / "candidate-v2.pkl"
    )

    save_candidate_v2_artifact(
        payload=artifact_payload,
        output_path=output_path,
    )

    with pytest.raises(
        ArtifactExistsError
    ):
        save_candidate_v2_artifact(
            payload=artifact_payload,
            output_path=output_path,
        )


def test_artifact_loads_only_with_correct_hash(
    tmp_path,
    artifact_payload,
):
    output_path = (
        tmp_path
        / "candidate-v2.pkl"
    )

    artifact_sha256 = (
        save_candidate_v2_artifact(
            payload=artifact_payload,
            output_path=output_path,
        )
    )

    runtime = (
        load_candidate_v2_artifact(
            artifact_path=output_path,
            expected_sha256=(
                artifact_sha256
            ),
        )
    )

    result = runtime.score(
        variable_name=(
            "opaque_value"
        ),
        value=TEST_SECRET,
    )

    assert result[
        "model"
    ] == "candidate-v2"

    assert result[
        "mode"
    ] == "advisory"

    assert result[
        "blocking"
    ] is False

    assert (
        0.0
        <= result[
            "risk_score"
        ]
        <= 1.0
    )


def test_tampered_artifact_is_rejected_before_load(
    tmp_path,
    artifact_payload,
):
    output_path = (
        tmp_path
        / "candidate-v2.pkl"
    )

    artifact_sha256 = (
        save_candidate_v2_artifact(
            payload=artifact_payload,
            output_path=output_path,
        )
    )

    with output_path.open(
        "ab"
    ) as handle:
        handle.write(
            b"tampered"
        )

    with pytest.raises(
        ArtifactIntegrityError
    ):
        load_candidate_v2_artifact(
            artifact_path=output_path,
            expected_sha256=(
                artifact_sha256
            ),
        )


def test_incompatible_locked_configuration_is_rejected(
    tmp_path,
    artifact_payload,
):
    invalid_payload = deepcopy(
        artifact_payload
    )

    invalid_payload[
        "locked_configuration"
    ][
        "threshold"
    ] = 0.99

    output_path = (
        tmp_path
        / "candidate-v2-invalid.pkl"
    )

    with pytest.raises(
        ArtifactCompatibilityError
    ):
        save_candidate_v2_artifact(
            payload=invalid_payload,
            output_path=output_path,
        )


def test_loaded_artifact_matches_original_runtime_score(
    tmp_path,
    artifact_payload,
):
    original_runtime = (
        load_runtime_from_payload(
            artifact_payload
        )
    )

    output_path = (
        tmp_path
        / "candidate-v2.pkl"
    )

    artifact_sha256 = (
        save_candidate_v2_artifact(
            payload=artifact_payload,
            output_path=output_path,
        )
    )

    loaded_runtime = (
        load_candidate_v2_artifact(
            artifact_path=output_path,
            expected_sha256=(
                artifact_sha256
            ),
        )
    )

    original = (
        original_runtime.score(
            variable_name=(
                "opaque_value"
            ),
            value=TEST_SECRET,
        )
    )

    loaded = (
        loaded_runtime.score(
            variable_name=(
                "opaque_value"
            ),
            value=TEST_SECRET,
        )
    )

    assert loaded[
        "risk_score"
    ] == pytest.approx(
        original[
            "risk_score"
        ]
    )


def load_runtime_from_payload(
    payload,
):
    from leakguard.ml.advisory import (
        CandidateV2AdvisoryRuntime,
    )

    return CandidateV2AdvisoryRuntime(
        context_model=payload[
            "context_model"
        ],
        text_model=payload[
            "text_model"
        ],
    )
