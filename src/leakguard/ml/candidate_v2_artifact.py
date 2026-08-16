import hashlib
import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from leakguard.ml.advisory import (
    MODEL_MODE,
    MODEL_NAME,
    CandidateV2AdvisoryRuntime,
    fit_candidate_v2_advisory_runtime,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
)


ARTIFACT_SCHEMA_VERSION = 1


class CandidateV2ArtifactError(Exception):
    """
    Base exception for Candidate v2
    artifact operations.
    """

    pass


class ArtifactIntegrityError(
    CandidateV2ArtifactError
):
    """
    Raised when artifact SHA-256 does not
    match its expected frozen identity.
    """

    pass


class ArtifactCompatibilityError(
    CandidateV2ArtifactError
):
    """
    Raised when an artifact does not match
    the current locked Candidate v2 runtime.
    """

    pass


class ArtifactExistsError(
    CandidateV2ArtifactError
):
    """
    Raised when an export would overwrite
    an existing frozen artifact.
    """

    pass


def sha256_file(
    path: Path,
) -> str:
    """
    Calculate SHA-256 without loading the
    complete file into memory.
    """

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def build_candidate_v2_artifact_payload(
    training_dataframe: pd.DataFrame,
    training_source: str,
    training_sha256: str,
) -> dict[str, Any]:
    """
    Fit Candidate v2 once and package only
    the runtime models and required metadata.

    The training dataframe itself is never
    stored inside the artifact payload.
    """

    runtime = (
        fit_candidate_v2_advisory_runtime(
            training_dataframe
        )
    )

    return {
        "schema_version": (
            ARTIFACT_SCHEMA_VERSION
        ),
        "model_name": MODEL_NAME,
        "mode": MODEL_MODE,
        "locked_configuration": {
            "text_weight": (
                LOCKED_TEXT_WEIGHT
            ),
            "context_weight": (
                LOCKED_CONTEXT_WEIGHT
            ),
            "threshold": (
                LOCKED_THRESHOLD
            ),
        },
        "training_identity": {
            "source": str(
                training_source
            ),
            "sha256": str(
                training_sha256
            ),
            "samples": len(
                training_dataframe
            ),
        },
        "context_model": (
            runtime.context_model
        ),
        "text_model": (
            runtime.text_model
        ),
    }


def validate_candidate_v2_artifact_payload(
    payload: Any,
) -> None:
    """
    Verify that a loaded payload is
    compatible with the locked Candidate v2
    implementation currently in the codebase.
    """

    if not isinstance(
        payload,
        dict,
    ):
        raise ArtifactCompatibilityError(
            "Candidate v2 artifact payload "
            "must be a dictionary."
        )

    required_keys = {
        "schema_version",
        "model_name",
        "mode",
        "locked_configuration",
        "training_identity",
        "context_model",
        "text_model",
    }

    missing = (
        required_keys
        - set(
            payload.keys()
        )
    )

    if missing:
        raise ArtifactCompatibilityError(
            "Candidate v2 artifact is missing: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    if (
        payload[
            "schema_version"
        ]
        != ARTIFACT_SCHEMA_VERSION
    ):
        raise ArtifactCompatibilityError(
            "Unsupported Candidate v2 "
            "artifact schema version."
        )

    if (
        payload[
            "model_name"
        ]
        != MODEL_NAME
    ):
        raise ArtifactCompatibilityError(
            "Unexpected Candidate v2 "
            "artifact model name."
        )

    if (
        payload[
            "mode"
        ]
        != MODEL_MODE
    ):
        raise ArtifactCompatibilityError(
            "Candidate v2 artifact must "
            "remain advisory."
        )

    locked = payload[
        "locked_configuration"
    ]

    expected_locked = {
        "text_weight": (
            LOCKED_TEXT_WEIGHT
        ),
        "context_weight": (
            LOCKED_CONTEXT_WEIGHT
        ),
        "threshold": (
            LOCKED_THRESHOLD
        ),
    }

    if locked != expected_locked:
        raise ArtifactCompatibilityError(
            "Candidate v2 artifact locked "
            "configuration does not match "
            "the current code."
        )

    training_identity = payload[
        "training_identity"
    ]

    if not isinstance(
        training_identity,
        dict,
    ):
        raise ArtifactCompatibilityError(
            "Candidate v2 artifact training "
            "identity is invalid."
        )

    for key in (
        "source",
        "sha256",
        "samples",
    ):
        if key not in training_identity:
            raise ArtifactCompatibilityError(
                "Candidate v2 artifact training "
                f"identity is missing {key}."
            )


def save_candidate_v2_artifact(
    payload: dict[str, Any],
    output_path: Path,
) -> str:
    """
    Save Candidate v2 as a frozen binary
    artifact.

    Existing artifacts are never overwritten.
    """

    validate_candidate_v2_artifact_payload(
        payload
    )

    if output_path.exists():
        raise ArtifactExistsError(
            "Candidate v2 artifact already "
            f"exists: {output_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "wb"
    ) as handle:
        pickle.dump(
            payload,
            handle,
            protocol=(
                pickle.HIGHEST_PROTOCOL
            ),
        )

    return sha256_file(
        output_path
    )


def load_candidate_v2_artifact(
    artifact_path: Path,
    expected_sha256: str,
) -> CandidateV2AdvisoryRuntime:
    """
    Load a trusted Candidate v2 artifact.

    SHA-256 is checked BEFORE unpickling.
    This ordering is security-critical.

    Never pass an expected hash obtained from
    the same untrusted artifact location.
    Production code must use a separately
    frozen artifact identity.
    """

    if not artifact_path.is_file():
        raise FileNotFoundError(
            f"Candidate v2 artifact not found: "
            f"{artifact_path}"
        )

    actual_sha256 = sha256_file(
        artifact_path
    )

    if actual_sha256 != expected_sha256:
        raise ArtifactIntegrityError(
            "Candidate v2 artifact SHA-256 "
            "does not match the expected "
            "frozen identity."
        )

    with artifact_path.open(
        "rb"
    ) as handle:
        payload = pickle.load(
            handle
        )

    validate_candidate_v2_artifact_payload(
        payload
    )

    return CandidateV2AdvisoryRuntime(
        context_model=payload[
            "context_model"
        ],
        text_model=payload[
            "text_model"
        ],
    )
