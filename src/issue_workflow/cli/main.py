"""CLI entry point for issue-workflow."""

from typing import Annotated

import typer

app = typer.Typer(
    name="issue-workflow",
    help="GitHub Issue-driven development workflow toolkit for Claude Code",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from issue_workflow import __version__

        typer.echo(f"issue-workflow {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Issue Workflow CLI - GitHub Issue-driven development toolkit."""
    pass


# Import and register commands
def _register_commands() -> None:
    """Register CLI commands."""
    from issue_workflow.cli.commands import init as init_cmd
    from issue_workflow.cli.commands import update as update_cmd

    app.add_typer(init_cmd.app, name="init")
    app.add_typer(update_cmd.app, name="update")


_register_commands()

if __name__ == "__main__":
    app()
