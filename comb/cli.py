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


# ------------------------------------------------------------------ #
# comb run
# ------------------------------------------------------------------ #

@app.command("run")
def run_goal(
    goal: str = typer.Argument(..., help="Natural language goal for the agent swarm"),
):
    """Plan and execute a multi-agent swarm for a given goal."""
    from comb.agents import plan, run

    console.print("[bold]Planning agents...[/bold]")
    try:
        agent_plan = plan(goal)
    except RuntimeError as e:
        rprint(f"[red]✗[/red] {e}")
        raise typer.Exit(1)

    rprint(f"[green]✓[/green] Plan: [bold]{len(agent_plan.agents)} agents[/bold]")
    for agent in agent_plan.agents:
        console.print(f"  [dim]·[/dim] {agent.role}  ({agent.provider} / {agent.model})")

    console.print("\n[bold]Running agents in parallel...[/bold]")
    results = run(agent_plan)
    results.sort(key=lambda r: r.role)

    console.print()
    for result in results:
        console.rule(f"[bold]{result.role}[/bold]  [dim]{result.provider}/{result.model}[/dim]")
        if result.error:
            rprint(f"[red]Error:[/red] {result.error}")
        else:
            console.print(result.output)
        console.print()




# ------------------------------------------------------------------ #
# comb serve
# ------------------------------------------------------------------ #

@app.command("serve")
def serve(
    host: str = typer.Option("localhost", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to listen on"),
):
    """Start the COMB web UI server."""
    import uvicorn
    rprint(f"[green]✓[/green] COMB server running at [bold]http://{host}:{port}[/bold]")
    uvicorn.run("comb.api.server:app", host=host, port=port, reload=False)


def main():
    app()