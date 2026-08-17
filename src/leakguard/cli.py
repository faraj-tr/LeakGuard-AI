from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from leakguard.config import (
    LeakGuardConfigError,
    load_leakguard_config,
    resolve_ml_advisory,
)
from leakguard.git_hook import (
    ExistingHookError,
    NotGitRepositoryError,
    install_pre_commit_hook,
)
from leakguard.ml.candidate_v2_runtime import (
    CandidateV2RuntimeError,
    load_frozen_candidate_v2_runtime,
)
from leakguard.model_cli import model_app
from leakguard.artifacts import scan_artifacts
from leakguard.scanner import scan_path
from leakguard.staged import (
    GitStagedScanError,
    scan_staged_path,
)
from leakguard.version import __version__


app = typer.Typer(
    help="LeakGuard AI - Vibe Coding Security Gate"
)

console = Console()

app.add_typer(
    model_app,
    name="model",
)


SEVERITY_STYLES = {
    "CRITICAL": "bold red",
    "HIGH": "red",
    "MEDIUM": "yellow",
    "LOW": "cyan",
}


@app.callback()
def main():
    """
    LeakGuard AI helps developers detect
    accidental secret exposure before
    insecure code reaches production.
    """

    pass


@app.command()
def version():
    """
    Display the current LeakGuard AI version.
    """

    console.print(
        Panel.fit(
            "[bold cyan]LeakGuard AI[/bold cyan]\n"
            f"[white]Version {__version__}[/white]\n\n"
            "[dim]"
            "Code fast with AI. "
            "Ship without leaking secrets."
            "[/dim]",
            title="Security Gate",
        )
    )


def format_file_location(
    file_path: str,
    root: Path,
    line_number: int,
) -> str:
    """
    Display project-relative file paths
    when possible.
    """

    file = Path(
        file_path
    )

    try:
        relative_path = (
            file.resolve()
            .relative_to(
                root.resolve()
            )
        )

        display_path = str(
            relative_path
        )

    except ValueError:
        display_path = str(
            file
        )

    return (
        f"{display_path}:"
        f"{line_number}"
    )


def format_ml_risk(
    finding: dict,
) -> str:
    """
    Format Candidate v2 advisory probability.

    The score is not presented as calibrated
    certainty and does not control blocking.
    """

    advisory = finding.get(
        "ml_advisory"
    )

    if advisory is None:
        return "-"

    risk_score = float(
        advisory[
            "risk_score"
        ]
    )

    prediction = advisory[
        "prediction"
    ]

    label = (
        "suspicious"
        if prediction
        == "suspicious"
        else "below-threshold"
    )

    return (
        f"{risk_score:.1%} "
        f"({label})"
    )


@app.command("install-hook")
def install_hook(
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help=(
            "Git repository where the "
            "LeakGuard pre-commit hook "
            "will be installed."
        ),
    )
):
    """
    Install LeakGuard as a Git
    pre-commit security gate.
    """

    try:
        hook_path = (
            install_pre_commit_hook(
                path
            )
        )

    except NotGitRepositoryError:

        console.print(
            Panel.fit(
                "[bold red]"
                "Git repository not found."
                "[/bold red]",
                title="Hook Installation",
            )
        )

        raise typer.Exit(
            code=1
        )

    except ExistingHookError as error:

        console.print(
            Panel.fit(
                "[bold yellow]"
                "Existing pre-commit hook detected."
                "[/bold yellow]\n\n"
                f"[dim]{error}[/dim]",
                title="Hook Installation",
            )
        )

        raise typer.Exit(
            code=1
        )

    console.print(
        Panel.fit(
            "[bold green]"
            "LeakGuard pre-commit hook installed."
            "[/bold green]\n\n"
            f"[dim]{hook_path}[/dim]\n\n"
            "Only staged Git changes will "
            "be checked before commits.",
            title="Git Security Gate",
        )
    )


@app.command()
def scan(
    path: Path = typer.Argument(
        ...,
        help="Project directory to scan",
    ),
    staged: bool = typer.Option(
        False,
        "--staged",
        help=(
            "Scan only the content staged "
            "for the next Git commit."
        ),
    ),
    ml_advisory: bool = typer.Option(
        False,
        "--ml-advisory",
        help=(
            "Force-enable the experimental "
            "Candidate v2 ML advisory signal."
        ),
    ),
    no_ml_advisory: bool = typer.Option(
        False,
        "--no-ml-advisory",
        help=(
            "Force-disable Candidate v2 "
            "ML advisory for this scan."
        ),
    ),
):
    """
    Scan a project for possible secret leaks.
    """

    if not path.exists():

        console.print(
            "[bold red]"
            "Error:"
            "[/bold red] "
            "Path does not exist."
        )

        raise typer.Exit(
            code=1
        )

    if not path.is_dir():

        console.print(
            "[bold red]"
            "Error:"
            "[/bold red] "
            "Please provide a directory."
        )

        raise typer.Exit(
            code=1
        )

    if (
        ml_advisory
        and no_ml_advisory
    ):

        console.print(
            Panel.fit(
                "[bold red]"
                "Conflicting ML options."
                "[/bold red]\n\n"
                "[dim]"
                "--ml-advisory and "
                "--no-ml-advisory cannot "
                "be used together."
                "[/dim]",
                title="Configuration",
            )
        )

        raise typer.Exit(
            code=2
        )

    if ml_advisory:
        cli_ml_override = True

    elif no_ml_advisory:
        cli_ml_override = False

    else:
        cli_ml_override = None

    try:
        configuration = (
            load_leakguard_config(
                path
            )
        )

    except LeakGuardConfigError as error:

        console.print(
            Panel.fit(
                "[bold red]"
                "Invalid LeakGuard "
                "configuration."
                "[/bold red]\n\n"
                f"[dim]{error}[/dim]",
                title="Configuration",
            )
        )

        raise typer.Exit(
            code=2
        )

    ml_advisory_enabled = (
        resolve_ml_advisory(
            cli_override=(
                cli_ml_override
            ),
            config=configuration,
        )
    )

    ml_runtime = None

    if ml_advisory_enabled:

        try:
            ml_runtime = (
                load_frozen_candidate_v2_runtime()
            )

        except CandidateV2RuntimeError as error:

            console.print(
                Panel.fit(
                    "[bold red]"
                    "Unable to enable "
                    "Candidate v2 ML advisory."
                    "[/bold red]\n\n"
                    f"[dim]{error}[/dim]\n\n"
                    "[dim]"
                    "The deterministic scanner "
                    "was not started."
                    "[/dim]",
                    title="ML Advisory",
                )
            )

            raise typer.Exit(
                code=2
            )

    console.print()

    mode_text = (
        "Scanning staged Git changes..."
        if staged
        else (
            "Scanning project for "
            "secret exposure..."
        )
    )

    console.print(
        Panel.fit(
            "[bold cyan]"
            "LeakGuard AI"
            "[/bold cyan]\n"
            f"[dim]{mode_text}[/dim]",
            title="Security Scan",
        )
    )

    if ml_advisory_enabled:

        console.print(
            "[dim]"
            "ML Advisory: Candidate v2 "
            "(experimental, non-blocking)"
            "[/dim]"
        )

    console.print()

    try:

        if staged:

            files_scanned, findings = (
                scan_staged_path(
                    path,
                    ml_advisory_runtime=(
                        ml_runtime
                    ),
                )
            )

        else:

            (
                source_files_scanned,
                source_findings,
            ) = scan_path(
                path,
                ml_advisory_runtime=(
                    ml_runtime
                ),
            )

            (
                artifact_files_scanned,
                artifact_findings,
            ) = scan_artifacts(
                path
            )

            files_scanned = (
                source_files_scanned
                + artifact_files_scanned
            )

            findings = (
                source_findings
                + artifact_findings
            )

    except GitStagedScanError as error:

        console.print(
            Panel.fit(
                "[bold red]"
                "Unable to scan staged changes."
                "[/bold red]\n\n"
                f"[dim]{error}[/dim]",
                title="Git Security Gate",
            )
        )

        raise typer.Exit(
            code=1
        )

    console.print(
        "Files scanned: "
        f"[bold]{files_scanned}[/bold]"
    )

    console.print(
        "Potential findings: "
        f"[bold]{len(findings)}[/bold]"
    )

    console.print()

    if not findings:

        console.print(
            Panel.fit(
                "[bold green]"
                "Security scan passed."
                "[/bold green]\n"
                "[dim]"
                "No suspicious secret exposure "
                "was detected."
                "[/dim]",
                title="Gate Result",
            )
        )

        return

    table = Table(
        title="Security Findings",
        show_lines=True,
    )

    table.add_column(
        "Severity",
        no_wrap=True,
    )

    table.add_column(
        "Finding",
    )

    table.add_column(
        "Location",
    )

    table.add_column(
        "Framework",
        no_wrap=True,
    )

    table.add_column(
        "Score",
        justify="right",
        no_wrap=True,
    )

    has_ml_results = any(
        finding.get(
            "ml_advisory"
        )
        is not None
        for finding in findings
    )

    if has_ml_results:
        table.add_column(
            "ML Risk",
            justify="right",
            no_wrap=True,
        )

    table.add_column(
        "Masked Value",
        no_wrap=True,
    )

    for finding in findings:

        severity = finding[
            "severity"
        ]

        severity_style = (
            SEVERITY_STYLES.get(
                severity,
                "white",
            )
        )

        location = (
            format_file_location(
                file_path=finding[
                    "file"
                ],
                root=path,
                line_number=finding[
                    "line"
                ],
            )
        )

        framework = (
            finding.get(
                "framework"
            )
            or "-"
        )

        candidate_score = (
            finding.get(
                "candidate_score"
            )
        )

        score = (
            "-"
            if candidate_score is None
            else str(
                candidate_score
            )
        )

        row = [
            (
                f"[{severity_style}]"
                f"{severity}"
                f"[/{severity_style}]"
            ),
            finding["type"],
            location,
            framework,
            score,
        ]

        if has_ml_results:
            row.append(
                format_ml_risk(
                    finding
                )
            )

        row.append(
            finding[
                "masked_value"
            ]
        )

        table.add_row(
            *row
        )

    console.print(
        table
    )

    findings_with_reasons = [
        finding
        for finding in findings
        if finding.get(
            "reasons"
        )
    ]

    if findings_with_reasons:

        console.print()

        console.print(
            "[bold]"
            "Detection Details"
            "[/bold]"
        )

        for finding in (
            findings_with_reasons
        ):

            location = (
                format_file_location(
                    file_path=finding[
                        "file"
                    ],
                    root=path,
                    line_number=finding[
                        "line"
                    ],
                )
            )

            reasons = " • ".join(
                finding[
                    "reasons"
                ]
            )

            console.print(
                f"[dim]{location}[/dim]\n"
                f"  {reasons}"
            )

    if has_ml_results:

        console.print()

        console.print(
            Panel.fit(
                "[bold cyan]"
                "Candidate v2 ML Advisory"
                "[/bold cyan]\n\n"
                "[dim]"
                "Experimental classification "
                "signal only.\n"
                "Risk scores are not calibrated "
                "credential probabilities.\n"
                "ML does not create, suppress, "
                "or escalate findings and has "
                "no independent blocking authority."
                "[/dim]",
                title="ML Advisory",
            )
        )

    critical_count = sum(
        finding["severity"]
        == "CRITICAL"
        for finding in findings
    )

    high_count = sum(
        finding["severity"]
        == "HIGH"
        for finding in findings
    )

    medium_count = sum(
        finding["severity"]
        == "MEDIUM"
        for finding in findings
    )

    console.print()

    console.print(
        Panel.fit(
            "[bold red]"
            "Security gate failed."
            "[/bold red]\n\n"
            "Critical: "
            f"[bold]{critical_count}[/bold]\n"
            "High: "
            f"[bold]{high_count}[/bold]\n"
            "Medium: "
            f"[bold]{medium_count}[/bold]\n\n"
            "[dim]"
            "Resolve the deterministic "
            "findings before shipping "
            "this project."
            "[/dim]",
            title="Gate Result",
        )
    )

    raise typer.Exit(
        code=1
    )


if __name__ == "__main__":
    app()
