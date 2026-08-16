import pytest

from leakguard.config import (
    LeakGuardConfigError,
    load_leakguard_config,
    resolve_ml_advisory,
)


def test_missing_config_uses_secure_defaults(
    tmp_path,
):
    config = load_leakguard_config(
        tmp_path
    )

    assert config.ml.enabled is False

    assert (
        config.ml.mode
        == "advisory"
    )

    assert config.source_path is None


def test_config_can_enable_ml_advisory(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            "enabled = true\n"
            'mode = "advisory"\n'
        ),
        encoding="utf-8",
    )

    config = load_leakguard_config(
        tmp_path
    )

    assert config.ml.enabled is True

    assert (
        config.ml.mode
        == "advisory"
    )

    assert (
        config.source_path
        == config_file
    )


def test_config_accepts_utf8_bom(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_bytes(
        (
            b"\xef\xbb\xbf"
            b"[ml]\n"
            b"enabled = true\n"
            b'mode = "advisory"\n'
        )
    )

    config = load_leakguard_config(
        tmp_path
    )

    assert config.ml.enabled is True

    assert (
        config.ml.mode
        == "advisory"
    )


def test_config_can_explicitly_disable_ml(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            "enabled = false\n"
        ),
        encoding="utf-8",
    )

    config = load_leakguard_config(
        tmp_path
    )

    assert config.ml.enabled is False

    assert (
        config.ml.mode
        == "advisory"
    )


def test_cli_true_override_has_priority(
    tmp_path,
):
    config = load_leakguard_config(
        tmp_path
    )

    assert (
        resolve_ml_advisory(
            cli_override=True,
            config=config,
        )
        is True
    )


def test_cli_false_override_has_priority(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            "enabled = true\n"
        ),
        encoding="utf-8",
    )

    config = load_leakguard_config(
        tmp_path
    )

    assert (
        resolve_ml_advisory(
            cli_override=False,
            config=config,
        )
        is False
    )


def test_config_value_is_used_without_cli_override(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            "enabled = true\n"
        ),
        encoding="utf-8",
    )

    config = load_leakguard_config(
        tmp_path
    )

    assert (
        resolve_ml_advisory(
            cli_override=None,
            config=config,
        )
        is True
    )


def test_blocking_ml_mode_is_rejected(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            "enabled = true\n"
            'mode = "blocking"\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        LeakGuardConfigError,
        match="only 'advisory'",
    ):
        load_leakguard_config(
            tmp_path
        )


def test_invalid_enabled_type_is_rejected(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            'enabled = "yes"\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        LeakGuardConfigError,
        match="true or false",
    ):
        load_leakguard_config(
            tmp_path
        )


def test_unknown_ml_key_is_rejected(
    tmp_path,
):
    config_file = (
        tmp_path
        / ".leakguard.toml"
    )

    config_file.write_text(
        (
            "[ml]\n"
            "enabled = true\n"
            "allow_blocking = true\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        LeakGuardConfigError,
        match="Unsupported",
    ):
        load_leakguard_config(
            tmp_path
        )
