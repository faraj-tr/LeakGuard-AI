import sys

from leakguard import runtime


def test_api_runtime_is_loopback_only(
    monkeypatch,
):
    captured = {}

    def fake_run(
        app,
        *,
        host,
        port,
    ):
        captured[
            "app"
        ] = app

        captured[
            "host"
        ] = host

        captured[
            "port"
        ] = port

    monkeypatch.setattr(
        runtime.uvicorn,
        "run",
        fake_run,
    )

    runtime.run_api()

    assert captured == {
        "app": (
            "leakguard.api.app:app"
        ),
        "host": "127.0.0.1",
        "port": 8000,
    }


def test_ui_runtime_targets_installed_app():
    app_path = (
        runtime.get_ui_app_path()
    )

    assert app_path.name == "app.py"

    assert (
        app_path.parent.name
        == "ui"
    )

    assert app_path.is_file()


def test_ui_runtime_is_loopback_only(
    monkeypatch,
):
    captured = {}

    def fake_run(
        command,
        *,
        check,
    ):
        captured[
            "command"
        ] = command

        captured[
            "check"
        ] = check

    monkeypatch.setattr(
        runtime.subprocess,
        "run",
        fake_run,
    )

    runtime.run_ui()

    command = captured[
        "command"
    ]

    assert command[0] == (
        sys.executable
    )

    assert command[1:4] == [
        "-m",
        "streamlit",
        "run",
    ]

    assert (
        "--server.address"
        in command
    )

    address_index = (
        command.index(
            "--server.address"
        )
    )

    assert (
        command[
            address_index + 1
        ]
        == "127.0.0.1"
    )

    port_index = (
        command.index(
            "--server.port"
        )
    )

    assert (
        command[
            port_index + 1
        ]
        == "8501"
    )

    assert captured[
        "check"
    ] is True
