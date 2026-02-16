"""Git operations helper."""

import subprocess
from pathlib import Path


class GitError(Exception):
    """Git operation error."""

    pass


class GitOperations:
    """Git operations wrapper."""

    def __init__(self, repo_path: Path | None = None) -> None:
        """Initialize with repository path."""
        self.repo_path = repo_path or Path.cwd()

    def _run(
        self, args: list[str], check: bool = True, capture_output: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run a git command."""
        try:
            return subprocess.run(
                ["git", *args],
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=check,
            )
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {e.stderr}") from e

    def get_current_branch(self) -> str:
        """Get current branch name."""
        result = self._run(["branch", "--show-current"])
        return result.stdout.strip()

    def branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists locally."""
        result = self._run(["branch", "--list", branch_name], check=False)
        return bool(result.stdout.strip())

    def create_branch(self, branch_name: str, start_point: str | None = None) -> None:
        """Create a new branch."""
        args = ["checkout", "-b", branch_name]
        if start_point:
            args.append(start_point)
        self._run(args)

    def checkout_branch(self, branch_name: str) -> None:
        """Checkout an existing branch."""
        self._run(["checkout", branch_name])

    def create_or_checkout_branch(self, branch_name: str, start_point: str | None = None) -> bool:
        """Create or checkout branch. Returns True if created, False if checked out."""
        if self.branch_exists(branch_name):
            self.checkout_branch(branch_name)
            return False
        self.create_branch(branch_name, start_point)
        return True

    def delete_branch(self, branch_name: str, force: bool = False) -> None:
        """Delete a local branch."""
        flag = "-D" if force else "-d"
        self._run(["branch", flag, branch_name])

    def get_project_name(self) -> str:
        """Get project name from repository directory."""
        return self.repo_path.name

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        result = self._run(["rev-parse", "--git-dir"], check=False)
        return result.returncode == 0

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        result = self._run(["status", "--porcelain"])
        return bool(result.stdout.strip())

    def worktree_add(self, path: Path, branch_name: str, new_branch: bool = True) -> None:
        """Add a new worktree."""
        args = ["worktree", "add"]
        if new_branch:
            args.extend(["-b", branch_name])
        args.append(str(path))
        if not new_branch:
            args.append(branch_name)
        self._run(args)

    def worktree_remove(self, path: Path, force: bool = False) -> None:
        """Remove a worktree."""
        args = ["worktree", "remove", str(path)]
        if force:
            args.append("--force")
        self._run(args)

    def worktree_list(self) -> list[dict[str, str]]:
        """List all worktrees."""
        result = self._run(["worktree", "list", "--porcelain"])
        worktrees: list[dict[str, str]] = []
        current: dict[str, str] = {}

        for line in result.stdout.strip().split("\n"):
            if not line:
                if current:
                    worktrees.append(current)
                    current = {}
                continue

            if line.startswith("worktree "):
                current["path"] = line[9:]
            elif line.startswith("branch "):
                current["branch"] = line[7:]
            elif line == "bare":
                current["bare"] = "true"
            elif line == "detached":
                current["detached"] = "true"

        if current:
            worktrees.append(current)

        return worktrees

    def worktree_prune(self) -> None:
        """Prune stale worktree information."""
        self._run(["worktree", "prune"])

    def get_default_branch(self) -> str:
        """Get default branch name from remote HEAD.

        Uses git symbolic-ref to detect the remote's default branch.
        If not set, attempts git remote set-head --auto to configure it.

        Returns:
            Default branch name (e.g., "main", "master", "develop").

        Raises:
            GitError: If default branch cannot be determined.
        """
        result = self._run(
            ["symbolic-ref", "refs/remotes/origin/HEAD"], check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().removeprefix("refs/remotes/origin/")

        set_head_result = self._run(
            ["remote", "set-head", "origin", "--auto"], check=False
        )
        if set_head_result.returncode == 0:
            retry = self._run(
                ["symbolic-ref", "refs/remotes/origin/HEAD"], check=False
            )
            if retry.returncode == 0 and retry.stdout.strip():
                return retry.stdout.strip().removeprefix("refs/remotes/origin/")

        raise GitError(
            "Cannot detect default branch. "
            "Ensure the remote 'origin' is configured and reachable."
        )

    def get_remote_url(self) -> str | None:
        """Get remote origin URL."""
        result = self._run(["remote", "get-url", "origin"], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
