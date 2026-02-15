"""Create-pr subcommand for issue-workflow CLI."""

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.cli.commands._common import build_log_result, on_tool_use
from issue_workflow.models.execution_log import ExecutionLog
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.execution_logger import LOG_BASE_DIR_NAME, ExecutionLogger

COMMAND_NAME: str = "create-pr"

EXIT_SUCCESS: int = 0


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
    # Dependency check
    check_dependencies([CLAUDE_DEPENDENCY])

    # Console output (escape brackets for Rich markup)
    mode_suffix = " (verbose mode)" if verbose else ""
    ui.console.print(f"\\[create-pr] Starting...{mode_suffix}")

    # Execute claude -p
    runner = ClaudeRunner()
    result = runner.run(
        "/commit-push-pr",
        cwd=None,
        timeout_seconds=timeout,
        verbose=verbose,
        on_tool_use=on_tool_use if verbose else None,
    )

    # Log execution
    log_result = build_log_result(result.raw_json, result.exit_code, timeout)
    entry = ExecutionLog(
        timestamp=datetime.now().astimezone(),
        command=COMMAND_NAME,
        args={},
        exit_code=result.exit_code,
        result=log_result,
    )
    try:
        logger = ExecutionLogger(base_dir=Path.cwd() / LOG_BASE_DIR_NAME)
        logger.log(entry)
    except OSError:
        ui.console.print("\\[create-pr] Warning: Failed to write log file.")

    # Done message
    ui.console.print(f"\\[create-pr] Done. (exit_code={result.exit_code})")

    return result.exit_code


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
