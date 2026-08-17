import tomllib
from pathlib import Path

from leakguard import __version__
from leakguard.api.app import (
    SERVICE_VERSION,
)


def test_package_exposes_version():
    assert __version__ == "0.1.0"


def test_api_uses_package_version():
    assert (
        SERVICE_VERSION
        == __version__
    )


def test_pyproject_uses_dynamic_version():
    project_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    pyproject_path = (
        project_root
        / "pyproject.toml"
    )

    data = tomllib.loads(
        pyproject_path.read_text(
            encoding="utf-8"
        )
    )

    project = data[
        "project"
    ]

    assert "version" not in project

    assert (
        "version"
        in project[
            "dynamic"
        ]
    )

    assert (
        data[
            "tool"
        ][
            "setuptools"
        ][
            "dynamic"
        ][
            "version"
        ][
            "attr"
        ]
        == (
            "leakguard.version."
            "__version__"
        )
    )


def test_product_entrypoints_are_declared():
    project_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    data = tomllib.loads(
        (
            project_root
            / "pyproject.toml"
        ).read_text(
            encoding="utf-8"
        )
    )

    scripts = (
        data[
            "project"
        ][
            "scripts"
        ]
    )

    assert scripts == {
        "leakguard": (
            "leakguard.cli:app"
        ),
        "leakguard-api": (
            "leakguard.runtime:run_api"
        ),
        "leakguard-ui": (
            "leakguard.runtime:run_ui"
        ),
    }
