"""Unit tests for Worktree naming."""

from pathlib import Path

import pytest

from issue_workflow.models.branch import Branch, BranchType
from issue_workflow.models.worktree import Worktree


class TestWorktreeNaming:
    """Tests for Worktree directory naming."""

    def test_directory_name_format(self) -> None:
        """Test worktree directory name follows format."""
        branch = Branch(
            type=BranchType.FEAT,
            issue_number=123,
            description="add-auth",
        )
        worktree = Worktree(
            path=Path("/home/user/project"),
            branch=branch,
            project_name="my-project",
        )
        assert worktree.directory_name == "my-project-feat-123-add-auth"

    def test_directory_name_replaces_slash(self) -> None:
        """Test worktree directory name replaces / with -."""
        branch = Branch(
            type=BranchType.FIX,
            issue_number=456,
            description="fix-bug",
        )
        worktree = Worktree(
            path=Path("/home/user/project"),
            branch=branch,
            project_name="project",
        )
        # Branch name is fix/456-fix-bug, should become fix-456-fix-bug
        assert worktree.directory_name == "project-fix-456-fix-bug"

    def test_full_path(self) -> None:
        """Test full path is in parent directory."""
        branch = Branch(
            type=BranchType.FEAT,
            issue_number=789,
            description="new-feature",
        )
        worktree = Worktree(
            path=Path("/home/user/project"),
            branch=branch,
            project_name="project",
        )
        # Full path should be in parent directory
        assert worktree.full_path == Path("/home/user/project-feat-789-new-feature")

    def test_from_branch(self) -> None:
        """Test creating worktree from branch."""
        branch = Branch(
            type=BranchType.REFACTOR,
            issue_number=101,
            description="cleanup",
        )
        worktree = Worktree.from_branch(
            repo_path=Path("/home/user/repo"),
            branch=branch,
            project_name="my-repo",
        )
        assert worktree.branch == branch
        assert worktree.project_name == "my-repo"
        assert worktree.path == Path("/home/user/repo")


class TestWorktreeExamples:
    """Test worktree naming examples from git-conventions.md."""

    @pytest.mark.parametrize(
        "branch_type,issue_number,description,expected_dir",
        [
            (BranchType.FEAT, 123, "add-auth", "project-feat-123-add-auth"),
            (BranchType.FIX, 456, "fix-login", "project-fix-456-fix-login"),
            (BranchType.REFACTOR, 789, "cleanup", "project-refactor-789-cleanup"),
        ],
    )
    def test_convention_examples(
        self,
        branch_type: BranchType,
        issue_number: int,
        description: str,
        expected_dir: str,
    ) -> None:
        """Test worktree naming follows convention examples."""
        branch = Branch(
            type=branch_type,
            issue_number=issue_number,
            description=description,
        )
        worktree = Worktree(
            path=Path("/home/user/project"),
            branch=branch,
            project_name="project",
        )
        assert worktree.directory_name == expected_dir
