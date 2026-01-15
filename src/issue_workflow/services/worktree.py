"""Worktree service for detection and cleanup."""

from pathlib import Path

from issue_workflow.lib.git import GitOperations


def find_worktree_for_branch(repo_path: Path, branch_name: str) -> Path | None:
    """Find worktree path for a branch.

    Args:
        repo_path: Repository root path
        branch_name: Branch name to search for

    Returns:
        Worktree path if found, None otherwise
    """
    git = GitOperations(repo_path)
    worktrees = git.worktree_list()

    for wt in worktrees:
        wt_branch = wt.get("branch", "")
        # Branch is stored as refs/heads/branch-name
        if wt_branch.endswith(branch_name) or wt_branch == f"refs/heads/{branch_name}":
            wt_path = wt.get("path")
            if wt_path:
                return Path(wt_path)

    return None


def cleanup_worktree(repo_path: Path, branch_name: str, force: bool = False) -> bool:
    """Remove worktree associated with a branch.

    Args:
        repo_path: Repository root path
        branch_name: Branch name whose worktree to remove
        force: Force removal even if worktree has changes

    Returns:
        True if worktree was removed, False if not found
    """
    worktree_path = find_worktree_for_branch(repo_path, branch_name)

    if worktree_path is None:
        return False

    git = GitOperations(repo_path)
    git.worktree_remove(worktree_path, force=force)
    git.worktree_prune()

    return True


def cleanup_branch_and_worktree(
    repo_path: Path, branch_name: str, force: bool = False
) -> dict[str, bool]:
    """Clean up both worktree and branch.

    Args:
        repo_path: Repository root path
        branch_name: Branch name to clean up
        force: Force removal

    Returns:
        Dict with 'worktree_removed' and 'branch_deleted' keys
    """
    result = {"worktree_removed": False, "branch_deleted": False}

    # Remove worktree first
    result["worktree_removed"] = cleanup_worktree(repo_path, branch_name, force)

    # Delete local branch
    git = GitOperations(repo_path)
    try:
        git.delete_branch(branch_name, force=force)
        result["branch_deleted"] = True
    except Exception:
        result["branch_deleted"] = False

    return result
