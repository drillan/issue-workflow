"""Merge-pr subcommand for issue-workflow CLI."""

from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.cli.commands._common import EXIT_SUCCESS, log_execution, on_tool_use
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.pr_detector import detect_pr_number

COMMAND_NAME: str = "merge-pr"


def _run_merge_pr(
    pr_number: int | None,
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the merge-pr command logic.

    Args:
        pr_number: PR number (None for auto-detection).
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Dependency check: gh only needed when pr_number not specified
    deps = [CLAUDE_DEPENDENCY]
    if pr_number is None:
        deps.append(GH_DEPENDENCY)
    check_dependencies(deps)

    # PR number detection
    resolved_pr = detect_pr_number(pr_number)

    # Console output
    mode_suffix = " (verbose mode)" if verbose else ""
    ui.console.print(f"\\[merge-pr] Starting...{mode_suffix}")

    # Execute claude -p (cwd=None: always run from main repository)
    runner = ClaudeRunner()
    result = runner.run(
        f"/merge-pr {resolved_pr}",
        cwd=None,
        timeout_seconds=timeout,
        verbose=verbose,
        on_tool_use=on_tool_use if verbose else None,
    )

    # Log execution
    log_execution(COMMAND_NAME, {"pr_number": resolved_pr}, result, timeout)

    # Done message
    ui.console.print(f"\\[merge-pr] Done. (exit_code={result.exit_code})")

    return result.exit_code


def merge_pr(
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
    """Merge a pull request after CI checks pass.

    Executes the /merge-pr skill via claude -p to wait for CI completion,
    merge the PR, and clean up branches/worktrees. Always runs from the
    main repository (not from a worktree).

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_merge_pr(
        pr_number=pr_number,
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
