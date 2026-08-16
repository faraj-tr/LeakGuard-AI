import os
from pathlib import Path


CANDIDATE_V2_ARTIFACT_FILENAME = (
    "candidate_v2_advisory_v1.pkl"
)


EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256 = (
    "a43e841c1b01468fe02fa084c3b665a9"
    "6f3d74b8bdb57a622697067c3f9e96e5"
)


MODEL_HOME_ENVIRONMENT_VARIABLE = (
    "LEAKGUARD_MODEL_HOME"
)


def get_candidate_v2_model_home() -> Path:
    """
    Return the local directory used for
    installed LeakGuard model artifacts.

    LEAKGUARD_MODEL_HOME may override the
    platform default for development,
    testing, or managed environments.
    """

    override = os.environ.get(
        MODEL_HOME_ENVIRONMENT_VARIABLE
    )

    if override:
        return (
            Path(override)
            .expanduser()
            .resolve()
        )

    if os.name == "nt":

        local_app_data = os.environ.get(
            "LOCALAPPDATA"
        )

        if local_app_data:
            return (
                Path(local_app_data)
                / "LeakGuardAI"
                / "models"
            )

        return (
            Path.home()
            / "AppData"
            / "Local"
            / "LeakGuardAI"
            / "models"
        )

    return (
        Path.home()
        / ".local"
        / "share"
        / "leakguard-ai"
        / "models"
    )


def get_candidate_v2_artifact_path() -> Path:
    """
    Return the installed Candidate v2
    artifact path.
    """

    return (
        get_candidate_v2_model_home()
        / CANDIDATE_V2_ARTIFACT_FILENAME
    )
