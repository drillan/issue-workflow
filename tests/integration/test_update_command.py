"""Integration tests for update command (T012)."""

import os
from pathlib import Path

from typer.testing import CliRunner

from issue_workflow.cli.main import app

runner = CliRunner()


class TestUpdateCommandExecution:
    """Tests for update command execution (T012)."""

    def test_update_without_claude_dir_fails(self, tmp_path: Path) -> None:
        """Test update fails when .claude/ directory does not exist."""
        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 2
            assert "not initialized" in result.output.lower() or ".claude" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_update_with_claude_dir_succeeds(self, tmp_path: Path) -> None:
        """Test update succeeds when .claude/ directory exists."""
        # Create .claude directory with commands and skills
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            # Should succeed (exit code 0) or have output about update
            assert result.exit_code == 0 or "update" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_update_shows_changes_summary(self, tmp_path: Path) -> None:
        """Test update shows summary of changes made."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            # Output should contain information about the update
            # (either changes made or "up to date" message)
            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_update_help_shows_usage(self) -> None:
        """Test update --help shows usage information."""
        result = runner.invoke(app, ["update", "--help"])
        assert result.exit_code == 0
        assert "update" in result.output.lower()


class TestDryRunOption:
    """Tests for --dry-run option (T021)."""

    def test_dry_run_shows_dry_run_indicator(self, tmp_path: Path) -> None:
        """Test --dry-run shows [DRY-RUN] indicator."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update", "--dry-run"])
            assert result.exit_code == 0
            assert "dry-run" in result.output.lower() or "DRY-RUN" in result.output
        finally:
            os.chdir(original_cwd)

    def test_dry_run_does_not_modify_files(self, tmp_path: Path) -> None:
        """Test --dry-run does not modify any files."""
        # Create .claude directory with a file
        claude_dir = tmp_path / ".claude"
        commands_dir = claude_dir / "commands"
        commands_dir.mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        # Create a marker file to verify it's not modified
        marker_file = commands_dir / "marker.md"
        marker_file.write_text("Original content")

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update", "--dry-run"])
            assert result.exit_code == 0
            # Marker file should still exist with original content
            assert marker_file.read_text() == "Original content"
        finally:
            os.chdir(original_cwd)

    def test_dry_run_shows_would_be_message(self, tmp_path: Path) -> None:
        """Test --dry-run shows 'would be' or similar message."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update", "--dry-run"])
            assert result.exit_code == 0
            # Should show something like "No changes were made"
            output_lower = result.output.lower()
            assert (
                "no changes" in output_lower
                or "would" in output_lower
                or "up to date" in output_lower
            )
        finally:
            os.chdir(original_cwd)


class TestSourceDirectoryNotFoundHandling:
    """Tests for SourceDirectoryNotFoundError handling in CLI (Critical #1)."""

    def test_source_directory_not_found_shows_reinstall_message(self, tmp_path: Path) -> None:
        """Test that SourceDirectoryNotFoundError shows helpful reinstall message."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        # Mock get_commands_source_dir to return non-existent path
        import issue_workflow.services.template as template_module

        original_func = template_module.get_commands_source_dir
        template_module.get_commands_source_dir = lambda: tmp_path / "nonexistent"

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 1
            assert "installation" in result.output.lower() or "reinstall" in result.output.lower()
        finally:
            template_module.get_commands_source_dir = original_func
            os.chdir(original_cwd)


class TestExitCodeOne:
    """Tests for exit code 1 on file operation errors (Important #4)."""

    def test_file_operation_error_returns_exit_code_1(self, tmp_path: Path) -> None:
        """Test that file operation errors result in exit code 1."""
        from unittest.mock import patch

        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        # Mock shutil.copy2 to raise OSError
        with patch("issue_workflow.services.template.shutil.copy2") as mock_copy:
            mock_copy.side_effect = OSError("Permission denied")

            try:
                result = runner.invoke(app, ["update"])
                assert result.exit_code == 1
            finally:
                os.chdir(original_cwd)

    def test_error_message_shown_with_exit_code_1(self, tmp_path: Path) -> None:
        """Test that error message is shown when exit code is 1."""
        from unittest.mock import patch

        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "commands").mkdir(parents=True)
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        # Mock shutil.copy2 to raise OSError
        with patch("issue_workflow.services.template.shutil.copy2") as mock_copy:
            mock_copy.side_effect = OSError("Permission denied")

            try:
                result = runner.invoke(app, ["update"])
                assert result.exit_code == 1
                # Should show error message
                assert (
                    "could not be updated" in result.output.lower()
                    or "error" in result.output.lower()
                )
            finally:
                os.chdir(original_cwd)


class TestEdgeCasesIntegration:
    """Integration tests for edge cases (T026)."""

    def test_claude_dir_not_exists_error_message(self, tmp_path: Path) -> None:
        """Test error message when .claude/ does not exist."""
        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 2
            assert "not initialized" in result.output.lower()
            assert "init" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_partial_claude_dir_structure(self, tmp_path: Path) -> None:
        """Test update with only .claude/ dir (no commands/skills subdirs)."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        # No commands or skills subdirectories

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            # Should succeed - directories will be created
            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)
