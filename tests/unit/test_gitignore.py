"""Unit tests for gitignore service."""

from pathlib import Path

from issue_workflow.services.gitignore import ensure_gitignore_entry

GITIGNORE_ENTRY = "/.issue-workflow/"
GITIGNORE_COMMENT = "# issue-workflow"


class TestEnsureGitignoreEntry:
    """Tests for ensure_gitignore_entry function."""

    def test_creates_gitignore_when_not_exists(self, tmp_path: Path) -> None:
        """Test .gitignore is created when it doesn't exist."""
        result = ensure_gitignore_entry(tmp_path)

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()
        assert result is True

    def test_new_gitignore_contains_entry(self, tmp_path: Path) -> None:
        """Test newly created .gitignore contains the entry."""
        ensure_gitignore_entry(tmp_path)

        content = (tmp_path / ".gitignore").read_text()
        assert GITIGNORE_ENTRY in content

    def test_new_gitignore_contains_comment(self, tmp_path: Path) -> None:
        """Test newly created .gitignore contains the section comment."""
        ensure_gitignore_entry(tmp_path)

        content = (tmp_path / ".gitignore").read_text()
        assert GITIGNORE_COMMENT in content

    def test_appends_to_existing_gitignore(self, tmp_path: Path) -> None:
        """Test entry is appended to existing .gitignore."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n.env\n")

        result = ensure_gitignore_entry(tmp_path)

        content = gitignore.read_text()
        assert GITIGNORE_ENTRY in content
        assert result is True

    def test_preserves_existing_content(self, tmp_path: Path) -> None:
        """Test existing .gitignore content is not destroyed."""
        gitignore = tmp_path / ".gitignore"
        original = "node_modules/\n.env\n__pycache__/\n"
        gitignore.write_text(original)

        ensure_gitignore_entry(tmp_path)

        content = gitignore.read_text()
        assert "node_modules/" in content
        assert ".env" in content
        assert "__pycache__/" in content

    def test_skips_when_entry_already_exists(self, tmp_path: Path) -> None:
        """Test entry is not duplicated if already present."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(f"node_modules/\n{GITIGNORE_ENTRY}\n")

        result = ensure_gitignore_entry(tmp_path)

        content = gitignore.read_text()
        assert content.count(GITIGNORE_ENTRY) == 1
        assert result is False

    def test_skips_when_entry_with_comment_already_exists(self, tmp_path: Path) -> None:
        """Test skips when full block (comment + entry) already present."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(f"node_modules/\n{GITIGNORE_COMMENT}\n{GITIGNORE_ENTRY}\n")

        result = ensure_gitignore_entry(tmp_path)

        content = gitignore.read_text()
        assert content.count(GITIGNORE_ENTRY) == 1
        assert result is False

    def test_adds_entry_even_with_partial_match(self, tmp_path: Path) -> None:
        """Test adds /.issue-workflow/ even if partial entry like .issue-workflow/logs exists."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(".issue-workflow/logs\n")

        result = ensure_gitignore_entry(tmp_path)

        content = gitignore.read_text()
        assert GITIGNORE_ENTRY in content
        assert result is True

    def test_handles_gitignore_without_trailing_newline(self, tmp_path: Path) -> None:
        """Test appends correctly when .gitignore has no trailing newline."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/")

        ensure_gitignore_entry(tmp_path)

        content = gitignore.read_text()
        # Entry should be on its own line, not concatenated
        lines = content.splitlines()
        assert GITIGNORE_ENTRY in lines
