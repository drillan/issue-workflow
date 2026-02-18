"""Create-pr subcommand for issue-workflow CLI."""

from typing import Annotated

import typer

from issue_workflow.cli.commands._common import EXIT_SUCCESS, run_claude_skill
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    check_dependencies,
)

COMMAND_NAME: str = "create-pr"


def _run_create_pr(
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the create-pr command logic.

    Args:
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    check_dependencies([CLAUDE_DEPENDENCY])

    return run_claude_skill(COMMAND_NAME, "/commit-push-pr", {}, verbose=verbose, timeout=timeout)


def create_pr(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show tool calls in real-time (stream-json)"),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Timeout in seconds for claude -p execution"),
    ] = DEFAULT_TIMEOUT_SECONDS,
) -> None:
    """Create a pull request (commit + push + PR).

    Executes the /commit-push-pr skill via claude -p.

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_create_pr(
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
