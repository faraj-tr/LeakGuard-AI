from leakguard.ml.candidate_v2_distribution import (
    CANDIDATE_V2_ARTIFACT_FILENAME,
    EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
    get_candidate_v2_artifact_path,
)


def test_distribution_identity_is_versioned():
    assert (
        CANDIDATE_V2_ARTIFACT_FILENAME
        == "candidate_v2_advisory_v1.pkl"
    )

    assert len(
        EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256
    ) == 64


def test_model_home_can_be_overridden(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv(
        "LEAKGUARD_MODEL_HOME",
        str(
            tmp_path
        ),
    )

    assert (
        get_candidate_v2_artifact_path()
        == (
            tmp_path.resolve()
            / CANDIDATE_V2_ARTIFACT_FILENAME
        )
    )
