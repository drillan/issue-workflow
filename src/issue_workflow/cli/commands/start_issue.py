"""Start-issue subcommand for issue-workflow CLI."""

from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.cli.commands._common import EXIT_SUCCESS, log_execution, on_tool_use
from issue_workflow.lib.git import GitError, GitOperations
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.worktree import (
    copy_hachimoku_to_worktree,
    find_worktree_for_branch,
)

COMMAND_NAME: str = "start-issue"

WORKTREE_BRANCH_PREFIX: str = "feat/"


def _prepare_worktree(issue_number: int) -> Path | None:
    """Prepare worktree for the given issue.

    Detects existing worktree or creates a new one.

    Args:
        issue_number: GitHub Issue number.

    Returns:
        Path to the worktree directory, or None if creation failed.
    """
    git = GitOperations()
    branch_name = f"{WORKTREE_BRANCH_PREFIX}{issue_number}-issue"

    existing = find_worktree_for_branch(git.repo_path, branch_name)
    if existing is not None:
        ui.print_info(f"Using existing worktree: {existing}")
        return existing

    worktree_path = git.repo_path.parent / f"{git.repo_path.name}-{branch_name.replace('/', '-')}"
    ui.print_info(f"Creating worktree: {worktree_path}")

    try:
        git.worktree_add(worktree_path, branch_name, new_branch=True)
    except GitError as e:
        ui.print_error(f"Failed to create worktree: {e}")
        return None

    copy_hachimoku_to_worktree(git.repo_path, worktree_path)

    return worktree_path


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
        if cwd is None:
            return 1

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
        on_tool_use=on_tool_use if verbose else None,
    )

    # Log execution
    log_execution(
        COMMAND_NAME,
        {"issue_number": issue_number, "worktree": worktree},
        result,
        timeout,
    )

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
