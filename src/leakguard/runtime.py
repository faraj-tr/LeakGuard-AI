import subprocess
import sys
from pathlib import Path

import uvicorn


API_HOST = "127.0.0.1"
API_PORT = 8000

UI_HOST = "127.0.0.1"
UI_PORT = 8501


def run_api() -> None:
    """
    Run the local-first LeakGuard FastAPI
    service.

    Network exposure is intentionally limited
    to loopback for the standard local
    entrypoint.
    """

    uvicorn.run(
        "leakguard.api.app:app",
        host=API_HOST,
        port=API_PORT,
    )


def get_ui_app_path() -> Path:
    """
    Return the installed Streamlit application
    path without depending on the current
    working directory.
    """

    return (
        Path(__file__)
        .resolve()
        .parent
        / "ui"
        / "app.py"
    )


def run_ui() -> None:
    """
    Run the local-first LeakGuard Streamlit
    dashboard using the active Python
    interpreter.
    """

    app_path = get_ui_app_path()

    if not app_path.is_file():
        raise RuntimeError(
            "LeakGuard dashboard application "
            "could not be located."
        )

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        UI_HOST,
        "--server.port",
        str(UI_PORT),
    ]

    subprocess.run(
        command,
        check=True,
    )
