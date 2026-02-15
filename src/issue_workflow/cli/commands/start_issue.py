"""Start-issue subcommand for issue-workflow CLI."""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.lib.git import GitOperations
from issue_workflow.models.execution_log import ExecutionLog
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.execution_logger import LOG_BASE_DIR_NAME, ExecutionLogger
from issue_workflow.services.worktree import (
    copy_hachimoku_to_worktree,
    find_worktree_for_branch,
)

COMMAND_NAME: str = "start-issue"

SECURITY_NOTICE: str = (
    "\n\n\u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass"
    " Claude Code's permission checks for automated execution."
    " Only run in trusted environments."
)

WORKTREE_BRANCH_PREFIX: str = "feat/"

EXIT_SUCCESS: int = 0


def _on_tool_use(name: str, input_str: str) -> None:
    """Print tool use event in verbose mode."""
    truncated = input_str[:80] + "..." if len(input_str) > 80 else input_str
    ui.console.print(f"\u25cf {name}({truncated})")


def _prepare_worktree(issue_number: int) -> Path:
    """Prepare worktree for the given issue.

    Detects existing worktree or creates a new one.

    Args:
        issue_number: GitHub Issue number.

    Returns:
        Path to the worktree directory.
    """
    git = GitOperations()
    branch_name = f"{WORKTREE_BRANCH_PREFIX}{issue_number}-issue"

    existing = find_worktree_for_branch(git.repo_path, branch_name)
    if existing is not None:
        ui.print_info(f"Using existing worktree: {existing}")
        return existing

    worktree_path = git.repo_path.parent / f"{git.repo_path.name}-{branch_name.replace('/', '-')}"
    ui.print_info(f"Creating worktree: {worktree_path}")
    git.worktree_add(worktree_path, branch_name, new_branch=True)
    copy_hachimoku_to_worktree(git.repo_path, worktree_path)

    return worktree_path


def _build_log_result(raw_json: str, exit_code: int, timeout: int) -> dict[str, object]:
    """Build the result dict for ExecutionLog.

    Args:
        raw_json: Raw JSON output from claude -p.
        exit_code: Process exit code.
        timeout: Timeout value in seconds.

    Returns:
        Parsed JSON dict or error info dict.
    """
    if exit_code == -1:
        return {"error": "timeout", "timeout_seconds": timeout}
    try:
        parsed: dict[str, object] = json.loads(raw_json)
        return parsed
    except (json.JSONDecodeError, TypeError):
        return {"error": "parse_error", "raw": raw_json}


def _run_start_issue(
    issue_number: int,
    worktree: bool,
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the start-issue command logic.

    Args:
        issue_number: GitHub Issue number.
        worktree: Whether to use worktree.
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Dependency check
    deps = [CLAUDE_DEPENDENCY]
    if worktree:
        deps.append(GH_DEPENDENCY)
    check_dependencies(deps)

    # Worktree preparation
    cwd: Path | None = None
    if worktree:
        cwd = _prepare_worktree(issue_number)

    # Console output (escape brackets for Rich markup)
    mode_suffix = " (verbose mode)" if verbose else ""
    ui.console.print(f"\\[start-issue] Starting...{mode_suffix}")

    # Execute claude -p
    runner = ClaudeRunner()
    result = runner.run(
        f"/start-issue {issue_number}",
        cwd=cwd,
        timeout_seconds=timeout,
        verbose=verbose,
        on_tool_use=_on_tool_use if verbose else None,
    )

    # Log execution
    log_result = _build_log_result(result.raw_json, result.exit_code, timeout)
    entry = ExecutionLog(
        timestamp=datetime.now().astimezone(),
        command=COMMAND_NAME,
        args={"issue_number": issue_number, "worktree": worktree},
        exit_code=result.exit_code,
        result=log_result,
    )
    logger = ExecutionLogger(base_dir=Path.cwd() / LOG_BASE_DIR_NAME)
    logger.log(entry)

    # Done message
    ui.console.print(f"\\[start-issue] Done. (exit_code={result.exit_code})")

    return result.exit_code


def start_issue(
    issue_number: Annotated[
        int,
        typer.Argument(help="GitHub Issue number"),
    ],
    worktree: Annotated[
        bool,
        typer.Option("--worktree", help="Create worktree and run skill there"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show tool calls in real-time (stream-json)"),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Timeout in seconds for claude -p execution"),
    ] = DEFAULT_TIMEOUT_SECONDS,
) -> None:
    """Start working on a GitHub Issue.

    Executes the /start-issue skill via claude -p.

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_start_issue(
        issue_number=issue_number,
        worktree=worktree,
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
