"""Unit tests for agent safety rules.

Validates that agent markdown files contain required safety rules
to prevent dangerous git operations.
"""

from pathlib import Path

import pytest

AGENTS_SOURCE_DIR = Path(__file__).parent.parent.parent / "src" / "issue_workflow" / "agents"

GIT_ADD_FORCE_RULE_KEYWORDS = ["git add -f", ".gitignore"]


class TestGitAddForceRule:
    """T125: Verify agents prohibit git add -f for .gitignore-excluded files."""

    @pytest.fixture()
    def pr_creator_content(self) -> str:
        """Read pr-creator.md agent file content."""
        return (AGENTS_SOURCE_DIR / "pr-creator.md").read_text()

    @pytest.fixture()
    def git_committer_content(self) -> str:
        """Read git-committer.md agent file content."""
        return (AGENTS_SOURCE_DIR / "git-committer.md").read_text()

    def test_pr_creator_prohibits_git_add_force(self, pr_creator_content: str) -> None:
        """pr-creator.md must contain a rule prohibiting git add -f."""
        for keyword in GIT_ADD_FORCE_RULE_KEYWORDS:
            assert keyword in pr_creator_content, (
                f"pr-creator.md missing '{keyword}' in safety rules"
            )

    def test_git_committer_prohibits_git_add_force(self, git_committer_content: str) -> None:
        """git-committer.md must contain a rule prohibiting git add -f."""
        for keyword in GIT_ADD_FORCE_RULE_KEYWORDS:
            assert keyword in git_committer_content, (
                f"git-committer.md missing '{keyword}' in safety rules"
            )

    def test_pr_creator_has_stop_on_gitignore_failure(self, pr_creator_content: str) -> None:
        """pr-creator.md must instruct to stop when git add fails due to .gitignore."""
        content_lower = pr_creator_content.lower()
        assert "report" in content_lower or "stop" in content_lower, (
            "pr-creator.md must instruct to report error and stop"
        )

    def test_git_committer_has_stop_on_gitignore_failure(self, git_committer_content: str) -> None:
        """git-committer.md must instruct to stop when git add fails due to .gitignore."""
        content_lower = git_committer_content.lower()
        assert "report" in content_lower or "stop" in content_lower, (
            "git-committer.md must instruct to report error and stop"
        )
