from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from leakguard.ml.candidate_v2_model_lifecycle import (
    CandidateV2ModelInstallError,
    get_candidate_v2_model_status,
    install_candidate_v2_artifact,
)


model_app = typer.Typer(
    help=(
        "Manage local LeakGuard "
        "machine-learning artifacts."
    )
)


console = Console()


@model_app.command("status")
def model_status():
    """
    Display Candidate v2 installation and
    integrity status.
    """

    status = (
        get_candidate_v2_model_status()
    )

    if status.runtime_ready:

        console.print(
            Panel.fit(
                "[bold green]"
                "Candidate v2 is installed "
                "and verified."
                "[/bold green]\n\n"
                f"State: {status.state}\n"
                "Mode: advisory\n"
                "Blocking authority: False\n"
                f"Path: {status.artifact_path}\n"
                "SHA-256: "
                f"{status.actual_sha256}",
                title="ML Model Status",
            )
        )

        return

    if not status.installed:

        console.print(
            Panel.fit(
                "[bold yellow]"
                "Candidate v2 is not installed."
                "[/bold yellow]\n\n"
                f"Expected location:\n"
                f"{status.artifact_path}\n\n"
                "[dim]"
                "Install a trusted frozen "
                "artifact before enabling "
                "--ml-advisory."
                "[/dim]",
                title="ML Model Status",
            )
        )

        raise typer.Exit(
            code=1
        )

    console.print(
        Panel.fit(
            "[bold red]"
            "Candidate v2 is not trusted."
            "[/bold red]\n\n"
            f"State: {status.state}\n"
            f"Path: {status.artifact_path}\n"
            "Expected SHA-256:\n"
            f"{status.expected_sha256}\n\n"
            "Actual SHA-256:\n"
            f"{status.actual_sha256}",
            title="ML Model Status",
        )
    )

    raise typer.Exit(
        code=2
    )


@model_app.command("install")
def model_install(
    artifact: Path = typer.Argument(
        ...,
        help=(
            "Path to a trusted prebuilt "
            "Candidate v2 artifact."
        ),
    )
):
    """
    Verify and install Candidate v2 locally.
    """

    try:
        status = (
            install_candidate_v2_artifact(
                source_path=artifact
            )
        )

    except CandidateV2ModelInstallError as error:

        console.print(
            Panel.fit(
                "[bold red]"
                "Candidate v2 installation "
                "was refused."
                "[/bold red]\n\n"
                f"[dim]{error}[/dim]",
                title="ML Model Installation",
            )
        )

        raise typer.Exit(
            code=2
        )

    console.print(
        Panel.fit(
            "[bold green]"
            "Candidate v2 is installed "
            "and verified."
            "[/bold green]\n\n"
            "Mode: advisory\n"
            "Blocking authority: False\n"
            f"Path: {status.artifact_path}\n"
            "SHA-256:\n"
            f"{status.actual_sha256}",
            title="ML Model Installation",
        )
    )
