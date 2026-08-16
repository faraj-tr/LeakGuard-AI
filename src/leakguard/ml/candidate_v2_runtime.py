from pathlib import Path

from leakguard.ml.advisory import (
    CandidateV2AdvisoryRuntime,
)
from leakguard.ml.candidate_v2_artifact import (
    ArtifactCompatibilityError,
    ArtifactIntegrityError,
    load_candidate_v2_artifact,
)


LEAKGUARD_REPOSITORY_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


DEFAULT_CANDIDATE_V2_ARTIFACT_PATH = (
    LEAKGUARD_REPOSITORY_ROOT
    / "models"
    / "candidate_v2_advisory_v1.pkl"
)


EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256 = (
    "a43e841c1b01468fe02fa084c3b665a9"
    "6f3d74b8bdb57a622697067c3f9e96e5"
)


class CandidateV2RuntimeError(Exception):
    """
    Raised when the frozen Candidate v2
    advisory runtime cannot be loaded.
    """

    pass


def load_frozen_candidate_v2_runtime(
    artifact_path: Path = (
        DEFAULT_CANDIDATE_V2_ARTIFACT_PATH
    ),
) -> CandidateV2AdvisoryRuntime:
    """
    Load the frozen Candidate v2 advisory
    artifact after verifying its trusted
    SHA-256 identity.

    SHA-256 verification occurs before
    unpickling inside the artifact loader.
    """

    try:
        return load_candidate_v2_artifact(
            artifact_path=artifact_path,
            expected_sha256=(
                EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256
            ),
        )

    except FileNotFoundError as error:
        raise CandidateV2RuntimeError(
            "Candidate v2 advisory artifact "
            "is not installed."
        ) from error

    except ArtifactIntegrityError as error:
        raise CandidateV2RuntimeError(
            "Candidate v2 advisory artifact "
            "failed SHA-256 integrity verification."
        ) from error

    except ArtifactCompatibilityError as error:
        raise CandidateV2RuntimeError(
            "Candidate v2 advisory artifact "
            "is incompatible with this "
            "LeakGuard version."
        ) from error
