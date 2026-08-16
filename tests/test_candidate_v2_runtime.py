from pathlib import Path

import pytest

from leakguard.ml.candidate_v2_runtime import (
    DEFAULT_CANDIDATE_V2_ARTIFACT_PATH,
    EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
    LEAKGUARD_REPOSITORY_ROOT,
    CandidateV2RuntimeError,
    load_frozen_candidate_v2_runtime,
)


def test_frozen_artifact_identity_is_sha256():
    assert len(
        EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256
    ) == 64

    int(
        EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
        16,
    )


def test_default_artifact_path_is_versioned():
    assert (
        DEFAULT_CANDIDATE_V2_ARTIFACT_PATH.name
        == "candidate_v2_advisory_v1.pkl"
    )

    assert (
        DEFAULT_CANDIDATE_V2_ARTIFACT_PATH.parent.name
        == "models"
    )


def test_default_artifact_path_is_absolute():
    assert (
        DEFAULT_CANDIDATE_V2_ARTIFACT_PATH
        .is_absolute()
    )

    assert (
        DEFAULT_CANDIDATE_V2_ARTIFACT_PATH
        == (
            LEAKGUARD_REPOSITORY_ROOT
            / "models"
            / "candidate_v2_advisory_v1.pkl"
        )
    )


def test_missing_frozen_artifact_has_safe_error(
    tmp_path,
):
    missing = (
        tmp_path
        / "missing-model.pkl"
    )

    with pytest.raises(
        CandidateV2RuntimeError,
        match="not installed",
    ):
        load_frozen_candidate_v2_runtime(
            artifact_path=missing
        )


def test_tampered_artifact_fails_integrity_before_load(
    tmp_path,
):
    tampered = (
        tmp_path
        / "candidate-v2.pkl"
    )

    tampered.write_bytes(
        b"not-a-trusted-model"
    )

    with pytest.raises(
        CandidateV2RuntimeError,
        match="SHA-256",
    ):
        load_frozen_candidate_v2_runtime(
            artifact_path=tampered
        )
