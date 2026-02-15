"""Respond-comments subcommand for issue-workflow CLI."""

from typing import Annotated

import typer

from issue_workflow.cli.commands._common import EXIT_SUCCESS, run_claude_skill
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.pr_detector import detect_pr_number

COMMAND_NAME: str = "respond-comments"


def _run_respond_comments(
    pr_number: int | None,
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the respond-comments command logic.

    Args:
        pr_number: PR number (None for auto-detection).
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    deps = [CLAUDE_DEPENDENCY]
    if pr_number is None:
        deps.append(GH_DEPENDENCY)
    check_dependencies(deps)

    resolved_pr = detect_pr_number(pr_number)

    return run_claude_skill(
        COMMAND_NAME,
        f"/review-pr-comments {resolved_pr}",
        {"pr_number": resolved_pr},
        verbose=verbose,
        timeout=timeout,
    )


def respond_comments(
    pr_number: Annotated[
        int | None,
        typer.Argument(help="PR number (auto-detected from current branch if omitted)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show tool calls in real-time (stream-json)"),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Timeout in seconds for claude -p execution"),
    ] = DEFAULT_TIMEOUT_SECONDS,
) -> None:
    """Respond to PR review comments from human reviewers.

    Executes the /review-pr-comments skill via claude -p to address
    review comments on a pull request.

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_respond_comments(
        pr_number=pr_number,
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
