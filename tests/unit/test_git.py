"""Unit tests for GitOperations class."""

import subprocess
from pathlib import Path

import pytest

from issue_workflow.lib.git import GitError, GitOperations


class TestGitOperationsInit:
    """Tests for GitOperations initialization."""

    def test_init_with_default_path(self) -> None:
        """Test initialization uses cwd by default."""
        git = GitOperations()
        assert git.repo_path == Path.cwd()

    def test_init_with_custom_path(self, temp_project_dir: Path) -> None:
        """Test initialization with custom path."""
        git = GitOperations(temp_project_dir)
        assert git.repo_path == temp_project_dir


class TestGitOperationsRun:
    """Tests for GitOperations._run method."""

    def test_run_successful_command(self, temp_git_repo: Path) -> None:
        """Test running successful git command."""
        git = GitOperations(temp_git_repo)
        result = git._run(["status"])
        assert result.returncode == 0

    def test_run_failed_command_raises_error(self, temp_git_repo: Path) -> None:
        """Test failed command raises GitError."""
        git = GitOperations(temp_git_repo)
        with pytest.raises(GitError, match="Git command failed"):
            git._run(["checkout", "nonexistent-branch"])

    def test_run_failed_command_check_false(self, temp_git_repo: Path) -> None:
        """Test failed command with check=False returns result."""
        git = GitOperations(temp_git_repo)
        result = git._run(["checkout", "nonexistent-branch"], check=False)
        assert result.returncode != 0


class TestGetCurrentBranch:
    """Tests for get_current_branch method."""

    def test_get_current_branch_on_main(self, temp_git_repo: Path) -> None:
        """Test getting current branch name."""
        git = GitOperations(temp_git_repo)
        # Create initial commit to establish branch
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        branch = git.get_current_branch()
        assert branch in ("main", "master")


class TestBranchExists:
    """Tests for branch_exists method."""

    def test_branch_exists_true(self, temp_git_repo: Path) -> None:
        """Test branch_exists returns True for existing branch."""
        git = GitOperations(temp_git_repo)
        # Setup: create commit and branch
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "branch", "test-branch"], cwd=temp_git_repo, check=True)

        assert git.branch_exists("test-branch") is True

    def test_branch_exists_false(self, temp_git_repo: Path) -> None:
        """Test branch_exists returns False for non-existing branch."""
        git = GitOperations(temp_git_repo)
        assert git.branch_exists("nonexistent") is False


class TestCreateBranch:
    """Tests for create_branch method."""

    def test_create_branch(self, temp_git_repo: Path) -> None:
        """Test creating a new branch."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        git.create_branch("new-branch")
        assert git.get_current_branch() == "new-branch"

    def test_create_branch_from_start_point(self, temp_git_repo: Path) -> None:
        """Test creating branch from specific start point."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        git.create_branch("feature-branch", "HEAD")
        assert git.branch_exists("feature-branch") is True


class TestCheckoutBranch:
    """Tests for checkout_branch method."""

    def test_checkout_existing_branch(self, temp_git_repo: Path) -> None:
        """Test checking out existing branch."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "branch", "other-branch"], cwd=temp_git_repo, check=True)

        git.checkout_branch("other-branch")
        assert git.get_current_branch() == "other-branch"

    def test_checkout_nonexistent_branch_raises_error(self, temp_git_repo: Path) -> None:
        """Test checking out non-existent branch raises GitError."""
        git = GitOperations(temp_git_repo)
        with pytest.raises(GitError):
            git.checkout_branch("nonexistent")


class TestCreateOrCheckoutBranch:
    """Tests for create_or_checkout_branch method."""

    def test_creates_new_branch(self, temp_git_repo: Path) -> None:
        """Test creates new branch when it doesn't exist."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        created = git.create_or_checkout_branch("new-branch")
        assert created is True
        assert git.get_current_branch() == "new-branch"

    def test_checks_out_existing_branch(self, temp_git_repo: Path) -> None:
        """Test checks out existing branch."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "branch", "existing"], cwd=temp_git_repo, check=True)

        created = git.create_or_checkout_branch("existing")
        assert created is False
        assert git.get_current_branch() == "existing"


class TestDeleteBranch:
    """Tests for delete_branch method."""

    def test_delete_branch(self, temp_git_repo: Path) -> None:
        """Test deleting a branch."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "branch", "to-delete"], cwd=temp_git_repo, check=True)

        git.delete_branch("to-delete")
        assert git.branch_exists("to-delete") is False

    def test_delete_branch_force(self, temp_git_repo: Path) -> None:
        """Test force deleting unmerged branch."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "checkout", "-b", "unmerged"], cwd=temp_git_repo, check=True)
        (temp_git_repo / "new.txt").write_text("new")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "unmerged"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "checkout", "-"], cwd=temp_git_repo, check=True)

        git.delete_branch("unmerged", force=True)
        assert git.branch_exists("unmerged") is False


class TestGetProjectName:
    """Tests for get_project_name method."""

    def test_get_project_name(self, temp_project_dir: Path) -> None:
        """Test getting project name from directory."""
        git = GitOperations(temp_project_dir)
        assert git.get_project_name() == "test-project"


class TestIsGitRepo:
    """Tests for is_git_repo method."""

    def test_is_git_repo_true(self, temp_git_repo: Path) -> None:
        """Test is_git_repo returns True for git repository."""
        git = GitOperations(temp_git_repo)
        assert git.is_git_repo() is True

    def test_is_git_repo_false(self, temp_project_dir: Path) -> None:
        """Test is_git_repo returns False for non-git directory."""
        git = GitOperations(temp_project_dir)
        assert git.is_git_repo() is False


class TestHasUncommittedChanges:
    """Tests for has_uncommitted_changes method."""

    def test_no_changes(self, temp_git_repo: Path) -> None:
        """Test returns False when no uncommitted changes."""
        git = GitOperations(temp_git_repo)
        # Create initial commit
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        assert git.has_uncommitted_changes() is False

    def test_has_untracked_file(self, temp_git_repo: Path) -> None:
        """Test returns True when there are untracked files."""
        git = GitOperations(temp_git_repo)
        (temp_git_repo / "new_file.txt").write_text("content")
        assert git.has_uncommitted_changes() is True

    def test_has_modified_file(self, temp_git_repo: Path) -> None:
        """Test returns True when there are modified files."""
        git = GitOperations(temp_git_repo)
        # Create initial commit
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        # Modify the file
        (temp_git_repo / "README.md").write_text("# Modified")
        assert git.has_uncommitted_changes() is True


class TestWorktreeOperations:
    """Tests for worktree-related methods."""

    def test_worktree_list_single(self, temp_git_repo: Path) -> None:
        """Test listing worktrees when only main worktree exists."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktrees = git.worktree_list()
        assert len(worktrees) == 1
        assert worktrees[0]["path"] == str(temp_git_repo)

    def test_worktree_add_and_list(self, temp_git_repo: Path) -> None:
        """Test adding and listing worktrees."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "worktree-test"
        git.worktree_add(worktree_path, "feature-branch")

        worktrees = git.worktree_list()
        assert len(worktrees) == 2

    def test_worktree_remove(self, temp_git_repo: Path) -> None:
        """Test removing a worktree."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "to-remove"
        git.worktree_add(worktree_path, "temp-branch")
        git.worktree_remove(worktree_path)

        worktrees = git.worktree_list()
        assert len(worktrees) == 1

    def test_worktree_add_existing_branch(self, temp_git_repo: Path) -> None:
        """Test adding worktree for existing branch."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "branch", "existing-branch"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "existing-wt"
        git.worktree_add(worktree_path, "existing-branch", new_branch=False)

        worktrees = git.worktree_list()
        assert len(worktrees) == 2

    def test_worktree_prune(self, temp_git_repo: Path) -> None:
        """Test worktree prune command runs successfully."""
        git = GitOperations(temp_git_repo)
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        # Should not raise any error
        git.worktree_prune()


class TestGetRemoteUrl:
    """Tests for get_remote_url method."""

    def test_get_remote_url_no_remote(self, temp_git_repo: Path) -> None:
        """Test returns None when no remote configured."""
        git = GitOperations(temp_git_repo)
        assert git.get_remote_url() is None

    def test_get_remote_url_with_remote(self, temp_git_repo: Path) -> None:
        """Test returns URL when remote is configured."""
        git = GitOperations(temp_git_repo)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/test/repo.git"],
            cwd=temp_git_repo,
            check=True,
        )
        assert git.get_remote_url() == "https://github.com/test/repo.git"
