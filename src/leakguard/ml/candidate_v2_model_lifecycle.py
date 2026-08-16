import shutil
from dataclasses import dataclass
from pathlib import Path

from leakguard.ml.candidate_v2_artifact import (
    ArtifactCompatibilityError,
    ArtifactIntegrityError,
    load_candidate_v2_artifact,
    sha256_file,
)
from leakguard.ml.candidate_v2_distribution import (
    EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
    get_candidate_v2_artifact_path,
)


class CandidateV2ModelInstallError(
    Exception
):
    """
    Raised when a Candidate v2 artifact
    cannot be safely installed.
    """

    pass


@dataclass(frozen=True)
class CandidateV2ModelStatus:
    artifact_path: Path
    state: str
    installed: bool
    integrity_verified: bool
    runtime_ready: bool
    expected_sha256: str
    actual_sha256: str | None


def get_candidate_v2_model_status(
    artifact_path: Path | None = None,
    expected_sha256: str = (
        EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256
    ),
) -> CandidateV2ModelStatus:
    """
    Inspect Candidate v2 installation state.

    Unpickling is attempted only after the
    artifact passes SHA-256 verification.
    """

    path = (
        get_candidate_v2_artifact_path()
        if artifact_path is None
        else Path(
            artifact_path
        )
    )

    if not path.is_file():
        return CandidateV2ModelStatus(
            artifact_path=path,
            state="missing",
            installed=False,
            integrity_verified=False,
            runtime_ready=False,
            expected_sha256=(
                expected_sha256
            ),
            actual_sha256=None,
        )

    actual_sha256 = sha256_file(
        path
    )

    if actual_sha256 != expected_sha256:
        return CandidateV2ModelStatus(
            artifact_path=path,
            state="integrity_failed",
            installed=True,
            integrity_verified=False,
            runtime_ready=False,
            expected_sha256=(
                expected_sha256
            ),
            actual_sha256=(
                actual_sha256
            ),
        )

    try:
        load_candidate_v2_artifact(
            artifact_path=path,
            expected_sha256=(
                expected_sha256
            ),
        )

    except (
        ArtifactCompatibilityError,
        ArtifactIntegrityError,
        ModuleNotFoundError,
        ImportError,
        AttributeError,
    ):
        return CandidateV2ModelStatus(
            artifact_path=path,
            state="incompatible",
            installed=True,
            integrity_verified=True,
            runtime_ready=False,
            expected_sha256=(
                expected_sha256
            ),
            actual_sha256=(
                actual_sha256
            ),
        )

    return CandidateV2ModelStatus(
        artifact_path=path,
        state="verified",
        installed=True,
        integrity_verified=True,
        runtime_ready=True,
        expected_sha256=(
            expected_sha256
        ),
        actual_sha256=(
            actual_sha256
        ),
    )


def install_candidate_v2_artifact(
    source_path: Path,
    target_path: Path | None = None,
    expected_sha256: str = (
        EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256
    ),
) -> CandidateV2ModelStatus:
    """
    Install a prebuilt trusted Candidate v2
    artifact into LeakGuard's local model
    directory.

    The source must pass SHA-256 verification
    before it is unpickled or copied.
    """

    source = (
        Path(source_path)
        .expanduser()
        .resolve()
    )

    if not source.is_file():
        raise CandidateV2ModelInstallError(
            "Candidate v2 artifact source "
            "does not exist."
        )

    source_sha256 = sha256_file(
        source
    )

    if source_sha256 != expected_sha256:
        raise CandidateV2ModelInstallError(
            "Candidate v2 artifact source "
            "failed trusted SHA-256 verification."
        )

    try:
        load_candidate_v2_artifact(
            artifact_path=source,
            expected_sha256=(
                expected_sha256
            ),
        )

    except (
        ArtifactCompatibilityError,
        ArtifactIntegrityError,
        ModuleNotFoundError,
        ImportError,
        AttributeError,
    ) as error:
        raise CandidateV2ModelInstallError(
            "Candidate v2 artifact source "
            "is not compatible with this "
            "LeakGuard version."
        ) from error

    destination = (
        get_candidate_v2_artifact_path()
        if target_path is None
        else (
            Path(target_path)
            .expanduser()
            .resolve()
        )
    )

    if destination.is_file():

        existing_status = (
            get_candidate_v2_model_status(
                artifact_path=destination,
                expected_sha256=(
                    expected_sha256
                ),
            )
        )

        if existing_status.runtime_ready:
            return existing_status

        raise CandidateV2ModelInstallError(
            "An untrusted or incompatible "
            "Candidate v2 artifact already "
            "exists at the destination. "
            "LeakGuard refuses to overwrite it."
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copyfile(
        source,
        destination,
    )

    copied_sha256 = sha256_file(
        destination
    )

    if copied_sha256 != expected_sha256:

        try:
            destination.unlink()
        except OSError:
            pass

        raise CandidateV2ModelInstallError(
            "Candidate v2 artifact integrity "
            "changed during installation."
        )

    status = (
        get_candidate_v2_model_status(
            artifact_path=destination,
            expected_sha256=(
                expected_sha256
            ),
        )
    )

    if not status.runtime_ready:
        raise CandidateV2ModelInstallError(
            "Candidate v2 artifact was copied "
            "but failed final validation."
        )

    return status
