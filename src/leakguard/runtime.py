import os
import subprocess
import sys
from pathlib import Path

import uvicorn


API_HOST = "127.0.0.1"
API_PORT = 8000

UI_HOST = "127.0.0.1"
UI_PORT = 8501

CONTAINER_UI_HOST = "0.0.0.0"

CONTAINER_MODE_ENV = (
    "LEAKGUARD_CONTAINER_MODE"
)


def build_api_command() -> list[str]:
    """
    Build the internal FastAPI process command.
    """

    return [
        sys.executable,
        "-m",
        "uvicorn",
        "leakguard.api.app:app",
        "--host",
        API_HOST,
        "--port",
        str(API_PORT),
    ]


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


def build_ui_command(
    *,
    host: str,
) -> list[str]:
    """
    Build the Streamlit process command.
    """

    app_path = get_ui_app_path()

    if not app_path.is_file():
        raise RuntimeError(
            "LeakGuard dashboard application "
            "could not be located."
        )

    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        host,
        "--server.port",
        str(UI_PORT),
        "--server.headless",
        "true",
        "--theme.base",
        "light",
        "--theme.primaryColor",
        "#206D00",
        "--theme.backgroundColor",
        "#F7F8F4",
        "--theme.secondaryBackgroundColor",
        "#FFFFFF",
        "--theme.textColor",
        "#131C26",
        "--theme.baseFontSize",
        "17",
        "--theme.baseFontWeight",
        "400",
        "--theme.baseRadius",
        "8px",
        "--theme.buttonRadius",
        "8px",
        "--theme.borderColor",
        "#E5E7EB",
        "--theme.showSidebarBorder",
        "true",
        "--theme.font",
        "sans-serif",
        "--theme.headingFont",
        "sans-serif",
        "--theme.codeFont",
        "monospace",
    ]


def run_api() -> None:
    """
    Run the local-first LeakGuard FastAPI
    service.

    The standard host entrypoint remains
    restricted to loopback.
    """

    uvicorn.run(
        "leakguard.api.app:app",
        host=API_HOST,
        port=API_PORT,
    )


def run_ui() -> None:
    """
    Run the standard local-first Streamlit
    dashboard.
    """

    subprocess.run(
        build_ui_command(
            host=UI_HOST
        ),
        check=True,
    )


def run_stack() -> None:
    """
    Run the container-specific LeakGuard stack.

    FastAPI remains internal loopback-only.
    Streamlit listens on the container network
    interface so Docker can publish only its
    UI port to the host.

    This entrypoint refuses to run unless
    container mode is explicitly enabled.
    """

    if os.environ.get(
        CONTAINER_MODE_ENV
    ) != "1":
        raise RuntimeError(
            "Container stack runtime requires "
            "LEAKGUARD_CONTAINER_MODE=1."
        )

    api_process = subprocess.Popen(
        build_api_command()
    )

    try:
        subprocess.run(
            build_ui_command(
                host=CONTAINER_UI_HOST
            ),
            check=True,
        )

    finally:
        if api_process.poll() is None:
            api_process.terminate()

            try:
                api_process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:
                api_process.kill()
                api_process.wait()
