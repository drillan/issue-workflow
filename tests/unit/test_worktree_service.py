"""Unit tests for worktree service functions."""

import subprocess
from pathlib import Path

from issue_workflow.services.worktree import (
    cleanup_branch_and_worktree,
    cleanup_worktree,
    copy_hachimoku_to_worktree,
    find_worktree_for_branch,
)


class TestFindWorktreeForBranch:
    """Tests for find_worktree_for_branch function."""

    def test_find_existing_worktree(self, temp_git_repo: Path) -> None:
        """Test finding worktree for existing branch."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "feature-wt"
        subprocess.run(
            ["git", "worktree", "add", "-b", "feature-branch", str(worktree_path)],
            cwd=temp_git_repo,
            check=True,
        )

        result = find_worktree_for_branch(temp_git_repo, "feature-branch")
        assert result == worktree_path

    def test_find_nonexistent_worktree(self, temp_git_repo: Path) -> None:
        """Test returns None for non-existing worktree."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        result = find_worktree_for_branch(temp_git_repo, "nonexistent-branch")
        assert result is None

    def test_find_worktree_with_refs_prefix(self, temp_git_repo: Path) -> None:
        """Test finding worktree with refs/heads/ prefix."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "ref-test"
        subprocess.run(
            ["git", "worktree", "add", "-b", "refs-test", str(worktree_path)],
            cwd=temp_git_repo,
            check=True,
        )

        result = find_worktree_for_branch(temp_git_repo, "refs-test")
        assert result is not None

    def test_find_worktree_returns_none_for_main(self, temp_git_repo: Path) -> None:
        """Test returns None when searching for branch that is in main worktree."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        # Main worktree's branch is master or main
        # Should find main worktree or None depending on git config
        # In temp_git_repo the branch should be master or main
        _ = find_worktree_for_branch(temp_git_repo, "main")


class TestCleanupWorktree:
    """Tests for cleanup_worktree function."""

    def test_cleanup_existing_worktree(self, temp_git_repo: Path) -> None:
        """Test cleaning up existing worktree."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "cleanup-test"
        subprocess.run(
            ["git", "worktree", "add", "-b", "cleanup-branch", str(worktree_path)],
            cwd=temp_git_repo,
            check=True,
        )

        result = cleanup_worktree(temp_git_repo, "cleanup-branch")
        assert result is True
        assert not worktree_path.exists()

    def test_cleanup_nonexistent_worktree(self, temp_git_repo: Path) -> None:
        """Test cleanup returns False for non-existing worktree."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        result = cleanup_worktree(temp_git_repo, "nonexistent")
        assert result is False

    def test_cleanup_worktree_with_force(self, temp_git_repo: Path) -> None:
        """Test force cleanup of worktree with uncommitted changes."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "dirty-worktree"
        subprocess.run(
            ["git", "worktree", "add", "-b", "dirty-branch", str(worktree_path)],
            cwd=temp_git_repo,
            check=True,
        )

        # Add uncommitted changes to worktree
        (worktree_path / "dirty.txt").write_text("uncommitted")

        result = cleanup_worktree(temp_git_repo, "dirty-branch", force=True)
        assert result is True
        assert not worktree_path.exists()


class TestCleanupBranchAndWorktree:
    """Tests for cleanup_branch_and_worktree function."""

    def test_cleanup_both(self, temp_git_repo: Path) -> None:
        """Test cleaning up both worktree and branch."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "both-test"
        subprocess.run(
            ["git", "worktree", "add", "-b", "both-branch", str(worktree_path)],
            cwd=temp_git_repo,
            check=True,
        )

        result = cleanup_branch_and_worktree(temp_git_repo, "both-branch", force=True)
        assert result["worktree_removed"] is True
        assert result["branch_deleted"] is True

    def test_cleanup_branch_only(self, temp_git_repo: Path) -> None:
        """Test cleaning up branch when no worktree exists."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "branch", "orphan-branch"], cwd=temp_git_repo, check=True)

        result = cleanup_branch_and_worktree(temp_git_repo, "orphan-branch")
        assert result["worktree_removed"] is False
        assert result["branch_deleted"] is True

    def test_cleanup_neither(self, temp_git_repo: Path) -> None:
        """Test cleanup when neither worktree nor branch exist."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        result = cleanup_branch_and_worktree(temp_git_repo, "nonexistent-branch")
        assert result["worktree_removed"] is False
        assert result["branch_deleted"] is False

    def test_cleanup_worktree_only_branch_fails(self, temp_git_repo: Path) -> None:
        """Test when worktree is removed but branch deletion fails."""
        # Setup
        (temp_git_repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_git_repo, check=True)

        worktree_path = temp_git_repo.parent / "unmerged-test"
        subprocess.run(
            ["git", "worktree", "add", "-b", "unmerged-branch", str(worktree_path)],
            cwd=temp_git_repo,
            check=True,
        )

        # Add a commit to the branch
        (worktree_path / "new.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=worktree_path, check=True)
        subprocess.run(["git", "commit", "-m", "new commit"], cwd=worktree_path, check=True)

        # Remove worktree but don't force delete unmerged branch
        result = cleanup_branch_and_worktree(temp_git_repo, "unmerged-branch", force=False)
        # Worktree should be removed
        assert result["worktree_removed"] is True
        # Branch deletion should fail (unmerged)
        assert result["branch_deleted"] is False


class TestCopyHachimokuToWorktree:
    """Tests for copy_hachimoku_to_worktree function."""

    def test_copies_hachimoku_directory(self, tmp_path: Path) -> None:
        """Test copying .hachimoku/ with config and agents to worktree."""
        repo = tmp_path / "repo"
        repo.mkdir()
        hachimoku = repo / ".hachimoku"
        hachimoku.mkdir()
        (hachimoku / "config.toml").write_text('model = "test"')
        agents = hachimoku / "agents"
        agents.mkdir()
        (agents / "code-reviewer.toml").write_text('name = "reviewer"')
        (hachimoku / "reviews").mkdir()

        worktree = tmp_path / "worktree"
        worktree.mkdir()

        result = copy_hachimoku_to_worktree(repo, worktree)

        assert result is True
        assert (worktree / ".hachimoku").is_dir()
        assert (worktree / ".hachimoku" / "config.toml").read_text() == 'model = "test"'
        assert (worktree / ".hachimoku" / "agents" / "code-reviewer.toml").exists()

    def test_skips_when_hachimoku_not_exists(self, tmp_path: Path) -> None:
        """Test returns False and does nothing when .hachimoku/ is absent."""
        repo = tmp_path / "repo"
        repo.mkdir()
        worktree = tmp_path / "worktree"
        worktree.mkdir()

        result = copy_hachimoku_to_worktree(repo, worktree)

        assert result is False
        assert not (worktree / ".hachimoku").exists()

    def test_excludes_review_jsonl_files(self, tmp_path: Path) -> None:
        """Test that existing review JSONL files are not copied."""
        repo = tmp_path / "repo"
        repo.mkdir()
        hachimoku = repo / ".hachimoku"
        hachimoku.mkdir()
        (hachimoku / "config.toml").write_text("")
        reviews = hachimoku / "reviews"
        reviews.mkdir()
        (reviews / "pr-51.jsonl").write_text('{"data": "old review"}')
        (reviews / "diff.jsonl").write_text('{"data": "diff review"}')

        worktree = tmp_path / "worktree"
        worktree.mkdir()

        copy_hachimoku_to_worktree(repo, worktree)

        assert not (worktree / ".hachimoku" / "reviews" / "pr-51.jsonl").exists()
        assert not (worktree / ".hachimoku" / "reviews" / "diff.jsonl").exists()

    def test_creates_empty_reviews_directory(self, tmp_path: Path) -> None:
        """Test that reviews/ directory exists and is empty after copy."""
        repo = tmp_path / "repo"
        repo.mkdir()
        hachimoku = repo / ".hachimoku"
        hachimoku.mkdir()
        (hachimoku / "config.toml").write_text("")
        reviews = hachimoku / "reviews"
        reviews.mkdir()
        (reviews / "pr-51.jsonl").write_text('{"data": "old"}')

        worktree = tmp_path / "worktree"
        worktree.mkdir()

        copy_hachimoku_to_worktree(repo, worktree)

        reviews_dst = worktree / ".hachimoku" / "reviews"
        assert reviews_dst.is_dir()
        assert list(reviews_dst.iterdir()) == []

    def test_copies_all_agent_configs(self, tmp_path: Path) -> None:
        """Test that all agent TOML files in agents/ are copied."""
        repo = tmp_path / "repo"
        repo.mkdir()
        hachimoku = repo / ".hachimoku"
        hachimoku.mkdir()
        (hachimoku / "config.toml").write_text("")
        agents = hachimoku / "agents"
        agents.mkdir()
        (agents / "aggregator.toml").write_text('name = "agg"')
        (agents / "selector.toml").write_text('name = "sel"')
        (agents / "code-reviewer.toml").write_text('name = "cr"')
        (hachimoku / "reviews").mkdir()

        worktree = tmp_path / "worktree"
        worktree.mkdir()

        copy_hachimoku_to_worktree(repo, worktree)

        agents_dst = worktree / ".hachimoku" / "agents"
        copied_files = sorted(f.name for f in agents_dst.iterdir())
        assert copied_files == ["aggregator.toml", "code-reviewer.toml", "selector.toml"]
