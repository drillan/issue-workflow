"""Push-changes subcommand for issue-workflow CLI."""

from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.cli.commands._common import EXIT_SUCCESS, run_claude_skill
from issue_workflow.lib.git import GitError
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.pr_detector import detect_pr_number

COMMAND_NAME: str = "push-changes"

PUSH_CHANGES_PROMPT: str = """/commit-push-pr

レビュー対応後の変更をコミットし、リモートにプッシュしてください。PRが既に存在する場合はPR作成をスキップしてください。"""


def _run_push_changes(
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the push-changes command logic.

    Args:
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    check_dependencies([CLAUDE_DEPENDENCY, GH_DEPENDENCY])

    # PR number auto-detection (FR-015a) for log filename
    try:
        pr_number = detect_pr_number()
    except (SystemExit, GitError):
        ui.print_error(
            "No PR found for current branch.\n\n"
            "Please create a PR first using 'issue-workflow create-pr'."
        )
        raise typer.Exit(code=1) from None

    return run_claude_skill(
        COMMAND_NAME,
        PUSH_CHANGES_PROMPT,
        {"pr_number": pr_number},
        verbose=verbose,
        timeout=timeout,
    )


def push_changes(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show tool calls in real-time (stream-json)"),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Timeout in seconds for claude -p execution"),
    ] = DEFAULT_TIMEOUT_SECONDS,
) -> None:
    """Push review changes (commit + push, skip PR creation).

    Executes the /commit-push-pr skill via claude -p with instructions
    to skip PR creation if a PR already exists.

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_push_changes(
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
