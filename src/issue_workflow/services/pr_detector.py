"""Service for detecting PR number from argument or current branch."""

from pathlib import Path

import typer

from issue_workflow.cli import ui
from issue_workflow.lib.git import GitOperations
from issue_workflow.services.github import get_pr_for_branch


def detect_pr_number(
    pr_number: int | None = None,
    *,
    cwd: Path | None = None,
) -> int:
    """Detect PR number from argument or current branch.

    Args:
        pr_number: Explicitly specified PR number (takes priority).
        cwd: Working directory for branch detection (e.g., worktree path).
            Defaults to current working directory.

    Returns:
        Detected PR number.

    Raises:
        typer.Exit: If no PR found and no number specified.
    """
    if pr_number is not None:
        return pr_number

    git = GitOperations(repo_path=cwd)
    branch_name = git.get_current_branch()
    result = get_pr_for_branch(branch_name)

    if not result.success or result.data is None:
        ui.print_error(
            f"No PR found for branch '{branch_name}'\n\n"
            "Please create a PR first, or specify a PR number explicitly."
        )
        raise typer.Exit(code=1)

    data = result.data
    if isinstance(data, dict):
        pr_num = data.get("number")
        if isinstance(pr_num, int):
            return pr_num

    ui.print_error(f"Could not extract PR number from response for branch '{branch_name}'")
    raise typer.Exit(code=1)
