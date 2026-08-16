from pathlib import Path

import pytest

from leakguard.ml.candidate_v2_distribution import (
    EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
)
from leakguard.ml.candidate_v2_runtime import (
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


def test_explicit_artifact_path_is_supported(
    tmp_path,
):
    missing = (
        tmp_path
        / "explicit-model.pkl"
    )

    assert isinstance(
        missing,
        Path,
    )

    with pytest.raises(
        CandidateV2RuntimeError
    ):
        load_frozen_candidate_v2_runtime(
            artifact_path=missing
        )


def test_runtime_error_does_not_expose_binary_content(
    tmp_path,
):
    artifact = (
        tmp_path
        / "candidate-v2.pkl"
    )

    artifact.write_bytes(
        b"dangerous-untrusted-content"
    )

    with pytest.raises(
        CandidateV2RuntimeError
    ) as error:
        load_frozen_candidate_v2_runtime(
            artifact_path=artifact
        )

    assert (
        "dangerous-untrusted-content"
        not in str(
            error.value
        )
    )
