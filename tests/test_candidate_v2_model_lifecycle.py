import pytest

from leakguard.ml.candidate_v2_artifact import (
    build_candidate_v2_artifact_payload,
    save_candidate_v2_artifact,
)
from leakguard.ml.candidate_v2_model_lifecycle import (
    CandidateV2ModelInstallError,
    get_candidate_v2_model_status,
    install_candidate_v2_artifact,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


@pytest.fixture(
    scope="module"
)
def training_dataframe():
    return (
        generate_synthetic_dataset_v3(
            samples_per_class=160,
            seed=1337,
        )
    )


@pytest.fixture
def trusted_test_artifact(
    tmp_path,
    training_dataframe,
):
    payload = (
        build_candidate_v2_artifact_payload(
            training_dataframe=(
                training_dataframe
            ),
            training_source="unit-test",
            training_sha256="unit-test",
        )
    )

    path = (
        tmp_path
        / "source.pkl"
    )

    artifact_sha256 = (
        save_candidate_v2_artifact(
            payload=payload,
            output_path=path,
        )
    )

    return (
        path,
        artifact_sha256,
    )


def test_missing_model_status(
    tmp_path,
):
    status = (
        get_candidate_v2_model_status(
            artifact_path=(
                tmp_path
                / "missing.pkl"
            ),
            expected_sha256="abc",
        )
    )

    assert status.state == "missing"
    assert status.installed is False
    assert status.runtime_ready is False


def test_verified_model_status(
    trusted_test_artifact,
):
    path, sha256 = (
        trusted_test_artifact
    )

    status = (
        get_candidate_v2_model_status(
            artifact_path=path,
            expected_sha256=sha256,
        )
    )

    assert status.state == "verified"
    assert status.integrity_verified is True
    assert status.runtime_ready is True


def test_install_copies_verified_artifact(
    tmp_path,
    trusted_test_artifact,
):
    source, sha256 = (
        trusted_test_artifact
    )

    destination = (
        tmp_path
        / "installed"
        / "candidate.pkl"
    )

    status = (
        install_candidate_v2_artifact(
            source_path=source,
            target_path=destination,
            expected_sha256=sha256,
        )
    )

    assert destination.exists()
    assert status.runtime_ready is True
    assert status.actual_sha256 == sha256


def test_install_is_idempotent_for_same_trusted_artifact(
    tmp_path,
    trusted_test_artifact,
):
    source, sha256 = (
        trusted_test_artifact
    )

    destination = (
        tmp_path
        / "candidate.pkl"
    )

    install_candidate_v2_artifact(
        source_path=source,
        target_path=destination,
        expected_sha256=sha256,
    )

    status = (
        install_candidate_v2_artifact(
            source_path=source,
            target_path=destination,
            expected_sha256=sha256,
        )
    )

    assert status.runtime_ready is True


def test_install_rejects_untrusted_source(
    tmp_path,
):
    source = (
        tmp_path
        / "untrusted.pkl"
    )

    source.write_bytes(
        b"untrusted-model"
    )

    with pytest.raises(
        CandidateV2ModelInstallError,
        match="SHA-256",
    ):
        install_candidate_v2_artifact(
            source_path=source,
            target_path=(
                tmp_path
                / "target.pkl"
            ),
            expected_sha256=(
                "0" * 64
            ),
        )


def test_install_refuses_overwriting_bad_existing_artifact(
    tmp_path,
    trusted_test_artifact,
):
    source, sha256 = (
        trusted_test_artifact
    )

    destination = (
        tmp_path
        / "candidate.pkl"
    )

    destination.write_bytes(
        b"wrong-existing-model"
    )

    with pytest.raises(
        CandidateV2ModelInstallError,
        match="refuses to overwrite",
    ):
        install_candidate_v2_artifact(
            source_path=source,
            target_path=destination,
            expected_sha256=sha256,
        )
