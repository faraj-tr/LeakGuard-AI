from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from leakguard.scanner import scan_path


app = typer.Typer(
    help="LeakGuard AI - Vibe Coding Security Gate"
)

console = Console()


@app.callback()
def main():
    """
    LeakGuard AI helps developers detect accidental secret exposure
    before insecure code reaches production.
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
            "[white]Version 0.1.0[/white]\n\n"
            "[dim]Code fast with AI. Ship without leaking secrets.[/dim]",
            title="Security Gate",
        )
    )


@app.command()
def scan(
    path: Path = typer.Argument(
        ...,
        help="Project directory to scan",
    )
):
    """
    Scan a project directory for possible secret leaks.
    """

    if not path.exists():
        console.print(
            "[bold red]Error:[/bold red] Path does not exist."
        )
        raise typer.Exit(code=1)

    if not path.is_dir():
        console.print(
            "[bold red]Error:[/bold red] Please provide a directory."
        )
        raise typer.Exit(code=1)

    console.print()

    console.print(
        Panel.fit(
            "[bold cyan]LeakGuard AI[/bold cyan]\n"
            "[dim]Scanning project for secret exposure...[/dim]",
            title="Security Scan",
        )
    )

    console.print()

    files_scanned, findings = scan_path(path)

    console.print(
        f"Files scanned: [bold]{files_scanned}[/bold]"
    )

    console.print(
        f"Potential findings: [bold]{len(findings)}[/bold]"
    )

    console.print()

    if not findings:

        console.print(
            "[bold green]✅ Security scan passed.[/bold green]"
        )

        return

    table = Table(
        title="Security Findings",
        show_lines=True,
    )

    table.add_column("Severity")
    table.add_column("Type")
    table.add_column("File")
    table.add_column("Line")
    table.add_column("Masked Value")

    for finding in findings:

        table.add_row(
            finding["severity"],
            finding["type"],
            finding["file"],
            str(finding["line"]),
            finding["masked_value"],
        )

    console.print(table)

    console.print()

    console.print(
        "[bold red]⚠ Potential secret exposure detected.[/bold red]"
    )


if __name__ == "__main__":
    app()