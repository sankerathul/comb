import typer

app = typer.Typer(
    name="comb",
    help="COMB — Collaborative Orchestration of Multi-agent Behavior.",
    no_args_is_help=True,
)

@app.command()
def version():
    """Show the current version of comb."""
    typer.echo("v0.1.0")

def main():
    app()