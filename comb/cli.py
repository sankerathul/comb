import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from comb.vault import vault
from comb.constants import SUPPORTED_PROVIDERS

app = typer.Typer(
    name="comb",
    help="COMB — Collaborative Orchestration of Multi-agent Behavior.",
    no_args_is_help=True,
)

console = Console()


# ------------------------------------------------------------------ #
# comb add
# ------------------------------------------------------------------ #

add_app = typer.Typer(help="Add a resource.", no_args_is_help=True)
app.add_typer(add_app, name="add")


@add_app.command("key")
def add_key(
    provider: str = typer.Argument(..., help="Provider name e.g. openai"),
    api_key: str = typer.Argument(..., help="Your API key"),
):
    """Store an API key for a provider."""
    if provider not in SUPPORTED_PROVIDERS:
        rprint(f"[red]✗[/red] Unknown provider '[bold]{provider}[/bold]'.")
        rprint(f"Supported: {', '.join(SUPPORTED_PROVIDERS)}")
        raise typer.Exit(1)

    vault.set(provider, api_key)
    rprint(f"[green]✓[/green] Key stored for [bold]{provider}[/bold].")


# ------------------------------------------------------------------ #
# comb list
# ------------------------------------------------------------------ #

list_app = typer.Typer(help="List resources.", no_args_is_help=True)
app.add_typer(list_app, name="list")


@list_app.command("keys")
def list_keys():
    """List all stored providers."""
    providers = vault.list()

    if not providers:
        rprint("[yellow]No keys stored yet.[/yellow]")
        rprint("Run: [bold]comb add key <provider> <api-key>[/bold]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Provider")
    table.add_column("Status")

    for p in sorted(providers):
        table.add_row(p, "[green]● stored[/green]")

    console.print(table)


# ------------------------------------------------------------------ #
# comb remove
# ------------------------------------------------------------------ #

remove_app = typer.Typer(help="Remove a resource.", no_args_is_help=True)
app.add_typer(remove_app, name="remove")


@remove_app.command("key")
def remove_key(
    provider: str = typer.Argument(..., help="Provider name to remove"),
):
    """Remove a stored API key."""
    if provider not in SUPPORTED_PROVIDERS:
        rprint(f"[red]✗[/red] Unknown provider '[bold]{provider}[/bold]'.")
        rprint(f"Supported: {', '.join(SUPPORTED_PROVIDERS)}")
        raise typer.Exit(1)

    removed = vault.delete(provider)
    if removed:
        rprint(f"[green]✓[/green] Key removed for [bold]{provider}[/bold].")
    else:
        rprint(f"[yellow]No key found for '[bold]{provider}[/bold]'.[/yellow]")
        raise typer.Exit(1)


def main():
    app()