"""GitHub CLI wrapper service."""

import json
import subprocess
from dataclasses import dataclass


@dataclass
class GhResult:
    """Result from gh CLI command."""

    success: bool
    data: dict[str, object] | list[dict[str, object]] | None
    error: str | None


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
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--json",
                "number,title,body,labels,state",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        data = json.loads(result.stdout)
        return GhResult(success=True, data=data, error=None)

    except json.JSONDecodeError as e:
        return GhResult(success=False, data=None, error=f"Invalid JSON response: {e}")
    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def get_pr(pr_number: int) -> GhResult:
    """Get pull request details from GitHub.

    Args:
        pr_number: PR number to fetch

    Returns:
        GhResult with PR data
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "view",
                str(pr_number),
                "--json",
                "number,title,state,mergeable,baseRefName,headRefName",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        data = json.loads(result.stdout)
        return GhResult(success=True, data=data, error=None)

    except json.JSONDecodeError as e:
        return GhResult(success=False, data=None, error=f"Invalid JSON response: {e}")
    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def wait_for_checks(pr_number: int, timeout: int = 600) -> GhResult:
    """Wait for PR checks to complete.

    Args:
        pr_number: PR number to wait for
        timeout: Timeout in seconds

    Returns:
        GhResult with check results
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "checks", str(pr_number), "--watch"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        return GhResult(success=True, data={"output": result.stdout}, error=None)

    except subprocess.TimeoutExpired:
        return GhResult(success=False, data=None, error="Timed out waiting for checks")
    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def merge_pr(pr_number: int, strategy: str = "squash", delete_branch: bool = True) -> GhResult:
    """Merge a pull request.

    Args:
        pr_number: PR number to merge
        strategy: Merge strategy (squash, merge, rebase)
        delete_branch: Whether to delete the branch after merge

    Returns:
        GhResult with merge result
    """
    args = ["gh", "pr", "merge", str(pr_number), f"--{strategy}"]
    if delete_branch:
        args.append("--delete-branch")

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        return GhResult(success=True, data={"output": result.stdout}, error=None)

    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def post_issue_comment(issue_number: int, body: str) -> GhResult:
    """Post a comment to an issue.

    Args:
        issue_number: Issue number to comment on
        body: Comment body

    Returns:
        GhResult with comment result
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "comment", str(issue_number), "--body", body],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        return GhResult(success=True, data={"output": result.stdout}, error=None)

    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def get_pr_comments(pr_number: int) -> GhResult:
    """Get review comments from a pull request.

    Args:
        pr_number: PR number to get comments from

    Returns:
        GhResult with comments data
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        data = json.loads(result.stdout)
        if isinstance(data, list):
            return GhResult(success=True, data=data, error=None)
        return GhResult(success=True, data=[data], error=None)

    except json.JSONDecodeError as e:
        return GhResult(success=False, data=None, error=f"Invalid JSON response: {e}")
    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))


def get_pr_for_branch(branch_name: str) -> GhResult:
    """Get PR associated with a branch.

    Args:
        branch_name: Branch name to search for

    Returns:
        GhResult with PR data
    """
    try:
        result = subprocess.run(
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
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return GhResult(success=False, data=None, error=result.stderr.strip())

        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            return GhResult(success=True, data=data[0], error=None)
        return GhResult(success=False, data=None, error="No PR found for branch")

    except json.JSONDecodeError as e:
        return GhResult(success=False, data=None, error=f"Invalid JSON response: {e}")
    except subprocess.SubprocessError as e:
        return GhResult(success=False, data=None, error=str(e))
