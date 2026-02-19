"""GitHub CLI wrapper service."""

import json
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GhResult:
    """Result from gh CLI command."""

    success: bool
    data: dict[str, object] | list[dict[str, object]] | None
    error: str | None


def _run_gh(
    cmd: list[str],
    *,
    parse_json: bool = True,
    timeout: int | None = None,
) -> GhResult:
    """Execute a gh CLI command and return the result.

    Args:
        cmd: Command and arguments to execute.
        parse_json: If True, parse stdout as JSON. If False, wrap stdout in dict.
        timeout: Timeout in seconds for subprocess execution.

    Returns:
        GhResult with command output or error details.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        if parse_json:
            data = json.loads(result.stdout)
            return GhResult(success=True, data=data, error=None)

        return GhResult(success=True, data={"output": result.stdout}, error=None)

    except subprocess.TimeoutExpired:
        return GhResult(success=False, data=None, error="Timed out waiting for checks")
    except json.JSONDecodeError as e:
        return GhResult(success=False, data=None, error=f"Invalid JSON response: {e}")
    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def check_gh_availability() -> tuple[bool, str]:
    """Check if gh CLI is available and authenticated.

    Returns:
        Tuple of (is_available, message)
    """
    # Check if gh is installed
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return False, (
                "GitHub CLI (gh) not found\n\n"
                "GitHub CLI is required to use Issue Workflow.\n\n"
                "Install: https://cli.github.com/"
            )
    except FileNotFoundError:
        return False, (
            "GitHub CLI (gh) not found\n\n"
            "GitHub CLI is required to use Issue Workflow.\n\n"
            "Install: https://cli.github.com/"
        )

    # Check if gh is authenticated
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() if result.stderr else ""
            hint = "Please authenticate with:\n  gh auth login"
            if detail:
                return False, f"GitHub CLI authentication failed\n\n{detail}\n\n{hint}"
            return False, f"GitHub CLI authentication failed\n\n{hint}"
    except subprocess.SubprocessError:
        return False, "Error occurred while checking GitHub CLI authentication"

    return True, "GitHub CLI is available and authenticated"


def get_issue(issue_number: int) -> GhResult:
    """Get issue details from GitHub.

    Args:
        issue_number: Issue number to fetch

    Returns:
        GhResult with issue data
    """
    return _run_gh(
        [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--json",
            "number,title,body,labels,state",
        ]
    )


def get_pr(pr_number: int) -> GhResult:
    """Get pull request details from GitHub.

    Args:
        pr_number: PR number to fetch

    Returns:
        GhResult with PR data
    """
    return _run_gh(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,title,state,mergeable,baseRefName,headRefName",
        ]
    )


def wait_for_checks(pr_number: int, timeout: int = 600) -> GhResult:
    """Wait for PR checks to complete.

    Args:
        pr_number: PR number to wait for
        timeout: Timeout in seconds

    Returns:
        GhResult with check results
    """
    return _run_gh(
        ["gh", "pr", "checks", str(pr_number), "--watch"],
        parse_json=False,
        timeout=timeout,
    )


def merge_pr(pr_number: int, strategy: str = "squash", delete_branch: bool = True) -> GhResult:
    """Merge a pull request.

    Args:
        pr_number: PR number to merge
        strategy: Merge strategy (squash, merge, rebase)
        delete_branch: Whether to delete the branch after merge

    Returns:
        GhResult with merge result
    """
    cmd = ["gh", "pr", "merge", str(pr_number), f"--{strategy}"]
    if delete_branch:
        cmd.append("--delete-branch")

    return _run_gh(cmd, parse_json=False)


def post_issue_comment(issue_number: int, body: str) -> GhResult:
    """Post a comment to an issue.

    Args:
        issue_number: Issue number to comment on
        body: Comment body

    Returns:
        GhResult with comment result
    """
    return _run_gh(
        ["gh", "issue", "comment", str(issue_number), "--body", body],
        parse_json=False,
    )


def get_pr_comments(pr_number: int) -> GhResult:
    """Get review comments from a pull request.

    Args:
        pr_number: PR number to get comments from

    Returns:
        GhResult with comments data
    """
    result = _run_gh(["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments"])
    if not result.success:
        return result
    if isinstance(result.data, list):
        return result
    if isinstance(result.data, dict):
        return GhResult(success=True, data=[result.data], error=None)
    return result


def get_pr_for_branch(branch_name: str) -> GhResult:
    """Get PR associated with a branch.

    Args:
        branch_name: Branch name to search for

    Returns:
        GhResult with PR data
    """
    result = _run_gh(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch_name,
            "--state",
            "open",
            "--json",
            "number,title,state,mergeable,baseRefName,headRefName",
            "--limit",
            "1",
        ]
    )
    if not result.success:
        return result
    if isinstance(result.data, list) and len(result.data) > 0:
        return GhResult(success=True, data=result.data[0], error=None)
    return GhResult(success=False, data=None, error="No PR found for branch")
