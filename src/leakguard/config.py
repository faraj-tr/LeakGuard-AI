from dataclasses import dataclass
from pathlib import Path
import tomllib


CONFIG_FILENAME = ".leakguard.toml"

SUPPORTED_ML_MODE = "advisory"


class LeakGuardConfigError(Exception):
    """
    Raised when LeakGuard configuration
    cannot be safely interpreted.
    """

    pass


@dataclass(frozen=True)
class MLConfig:
    """
    Candidate v2 configuration.

    Advisory is currently the only supported
    ML authority mode.
    """

    enabled: bool = False
    mode: str = SUPPORTED_ML_MODE


@dataclass(frozen=True)
class LeakGuardConfig:
    """
    Parsed project configuration.
    """

    ml: MLConfig
    source_path: Path | None


def read_toml_config(
    config_path: Path,
) -> dict:
    """
    Read TOML configuration as UTF-8.

    UTF-8 BOM is tolerated intentionally
    because Windows PowerShell may emit it
    when creating text files.

    Invalid encoding or TOML syntax is
    reported as a safe configuration error.
    """

    try:
        raw_content = config_path.read_bytes()

    except OSError as error:
        raise LeakGuardConfigError(
            "Unable to read .leakguard.toml."
        ) from error

    try:
        text = raw_content.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError as error:
        raise LeakGuardConfigError(
            ".leakguard.toml must use UTF-8 "
            "encoding."
        ) from error

    try:
        return tomllib.loads(
            text
        )

    except tomllib.TOMLDecodeError as error:
        raise LeakGuardConfigError(
            "Invalid .leakguard.toml syntax."
        ) from error


def load_leakguard_config(
    root: Path,
) -> LeakGuardConfig:
    """
    Load .leakguard.toml from a project.

    Missing configuration is valid and
    preserves the secure default:
    ML advisory disabled.
    """

    project_root = (
        Path(root)
        .expanduser()
        .resolve()
    )

    config_path = (
        project_root
        / CONFIG_FILENAME
    )

    if not config_path.is_file():
        return LeakGuardConfig(
            ml=MLConfig(),
            source_path=None,
        )

    data = read_toml_config(
        config_path
    )

    ml_data = data.get(
        "ml",
        {},
    )

    if not isinstance(
        ml_data,
        dict,
    ):
        raise LeakGuardConfigError(
            "[ml] must be a TOML table."
        )

    allowed_ml_keys = {
        "enabled",
        "mode",
    }

    unknown_ml_keys = (
        set(
            ml_data.keys()
        )
        - allowed_ml_keys
    )

    if unknown_ml_keys:
        raise LeakGuardConfigError(
            "Unsupported [ml] configuration "
            "key(s): "
            + ", ".join(
                sorted(
                    unknown_ml_keys
                )
            )
        )

    enabled = ml_data.get(
        "enabled",
        False,
    )

    if type(enabled) is not bool:
        raise LeakGuardConfigError(
            "[ml].enabled must be true "
            "or false."
        )

    mode = ml_data.get(
        "mode",
        SUPPORTED_ML_MODE,
    )

    if not isinstance(
        mode,
        str,
    ):
        raise LeakGuardConfigError(
            "[ml].mode must be a string."
        )

    if mode != SUPPORTED_ML_MODE:
        raise LeakGuardConfigError(
            "Unsupported ML mode. "
            "Candidate v2 supports only "
            "'advisory'."
        )

    return LeakGuardConfig(
        ml=MLConfig(
            enabled=enabled,
            mode=mode,
        ),
        source_path=config_path,
    )


def resolve_ml_advisory(
    cli_override: bool | None,
    config: LeakGuardConfig,
) -> bool:
    """
    Resolve whether ML advisory should run.

    Explicit CLI options have priority over
    project configuration.
    """

    if cli_override is not None:
        return cli_override

    return config.ml.enabled
