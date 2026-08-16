from pathlib import Path

from leakguard.ml.advisory import (
    CandidateV2AdvisoryRuntime,
)
from leakguard.ml.candidate_v2_artifact import (
    ArtifactCompatibilityError,
    ArtifactIntegrityError,
    load_candidate_v2_artifact,
)
from leakguard.ml.candidate_v2_distribution import (
    EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
    get_candidate_v2_artifact_path,
)


class CandidateV2RuntimeError(Exception):
    """
    Raised when the frozen Candidate v2
    advisory runtime cannot be loaded.
    """

    pass


def load_frozen_candidate_v2_runtime(
    artifact_path: Path | None = None,
) -> CandidateV2AdvisoryRuntime:
    """
    Load the trusted Candidate v2 advisory
    artifact.

    The expected SHA-256 identity is frozen
    in LeakGuard code and verification occurs
    before unpickling.
    """

    resolved_path = (
        get_candidate_v2_artifact_path()
        if artifact_path is None
        else Path(
            artifact_path
        )
    )

    try:
        return load_candidate_v2_artifact(
            artifact_path=resolved_path,
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
