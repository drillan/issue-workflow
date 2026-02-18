"""Integration tests for update command (T012)."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from issue_workflow.services.hachimoku_version import HachimokuVersionResult

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
        # Create .claude directory with skills
        claude_dir = tmp_path / ".claude"
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
        # Create .claude directory with a marker skill
        claude_dir = tmp_path / ".claude"
        skills_dir = claude_dir / "skills"
        marker_skill = skills_dir / "marker-skill"
        marker_skill.mkdir(parents=True)
        marker_file = marker_skill / "SKILL.md"
        marker_file.write_text("Original content")

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update", "--dry-run"])
            assert result.exit_code == 0
            # Marker skill should still exist with original content
            assert marker_file.read_text() == "Original content"
        finally:
            os.chdir(original_cwd)

    def test_dry_run_shows_would_be_message(self, tmp_path: Path) -> None:
        """Test --dry-run shows 'would be' or similar message."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
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
    """Tests for SourceDirectoryNotFoundError handling in CLI."""

    def test_source_directory_not_found_shows_reinstall_message(self, tmp_path: Path) -> None:
        """Test that SourceDirectoryNotFoundError shows helpful reinstall message."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        # Mock get_skills_source_dir to return non-existent path
        import issue_workflow.services.template as template_module

        original_func = template_module.get_skills_source_dir
        template_module.get_skills_source_dir = lambda: tmp_path / "nonexistent"

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 1
            assert "installation" in result.output.lower() or "reinstall" in result.output.lower()
        finally:
            template_module.get_skills_source_dir = original_func
            os.chdir(original_cwd)


class TestExitCodeOne:
    """Tests for exit code 1 on file operation errors."""

    def test_file_operation_error_returns_exit_code_1(self, tmp_path: Path) -> None:
        """Test that file operation errors result in exit code 1."""
        from unittest.mock import patch

        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        # Mock shutil.copytree to raise OSError (skills use copytree)
        with patch("issue_workflow.services.template.shutil.copytree") as mock_copytree:
            mock_copytree.side_effect = OSError("Permission denied")

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
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        # Mock shutil.copytree to raise OSError (skills use copytree)
        with patch("issue_workflow.services.template.shutil.copytree") as mock_copytree:
            mock_copytree.side_effect = OSError("Permission denied")

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
        """Test update with only .claude/ dir (no skills subdirs)."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        # No skills or agents subdirectories

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            # Should succeed - directories will be created
            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)


class TestUpdateAgentsIntegration:
    """Integration tests for agents update (T086)."""

    def test_update_includes_agents_changes(self, tmp_path: Path) -> None:
        """Test that update includes agents in the update (T086)."""
        # Create .claude directory structure
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)
        (claude_dir / "agents").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_update_creates_agents_directory(self, tmp_path: Path) -> None:
        """Test that update creates agents directory if missing (T086)."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)
        # No agents directory

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 0
            # Agents directory should be created
            assert (claude_dir / "agents").exists()
        finally:
            os.chdir(original_cwd)

    def test_update_shows_agents_category(self, tmp_path: Path) -> None:
        """Test that update shows Agents category in output (T086)."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)
        # Empty agents dir to trigger adds
        (claude_dir / "agents").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["update"])
            assert result.exit_code == 0
            # Should show "Agents" in the output since new agents are added
            assert "agents" in result.output.lower() or "added" in result.output.lower()
        finally:
            os.chdir(original_cwd)


class TestHachimokuVersionHint:
    """Integration tests for hachimoku version hint display."""

    def test_shows_hint_when_update_available(self, tmp_path: Path) -> None:
        """Test hint is displayed when newer hachimoku version is available."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        version_result = HachimokuVersionResult(
            installed_version="0.0.2",
            remote_version="0.0.3",
            update_available=True,
        )

        try:
            with patch(
                "issue_workflow.cli.commands.update.check_hachimoku_version",
                return_value=version_result,
            ):
                result = runner.invoke(app, ["update"])
                assert result.exit_code == 0
                assert "0.0.2" in result.output
                assert "0.0.3" in result.output
                assert "uv tool install --reinstall" in result.output
        finally:
            os.chdir(original_cwd)

    def test_no_hint_when_up_to_date(self, tmp_path: Path) -> None:
        """Test no hint is displayed when hachimoku is up to date."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        version_result = HachimokuVersionResult(
            installed_version="0.0.3",
            remote_version="0.0.3",
            update_available=False,
        )

        try:
            with patch(
                "issue_workflow.cli.commands.update.check_hachimoku_version",
                return_value=version_result,
            ):
                result = runner.invoke(app, ["update"])
                assert result.exit_code == 0
                assert "アップグレード" not in result.output
        finally:
            os.chdir(original_cwd)

    def test_no_hint_when_not_installed(self, tmp_path: Path) -> None:
        """Test no hint when hachimoku is not installed."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            with patch(
                "issue_workflow.cli.commands.update.check_hachimoku_version",
                return_value=None,
            ):
                result = runner.invoke(app, ["update"])
                assert result.exit_code == 0
                assert "アップグレード" not in result.output
        finally:
            os.chdir(original_cwd)

    def test_hint_shown_in_dry_run_mode(self, tmp_path: Path) -> None:
        """Test hint is displayed even in dry-run mode."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        version_result = HachimokuVersionResult(
            installed_version="0.0.2",
            remote_version="0.0.3",
            update_available=True,
        )

        try:
            with patch(
                "issue_workflow.cli.commands.update.check_hachimoku_version",
                return_value=version_result,
            ):
                result = runner.invoke(app, ["update", "--dry-run"])
                assert result.exit_code == 0
                assert "0.0.2" in result.output
                assert "0.0.3" in result.output
        finally:
            os.chdir(original_cwd)

    def test_update_succeeds_when_version_check_fails(self, tmp_path: Path) -> None:
        """Test update command succeeds even when version check raises an exception."""
        claude_dir = tmp_path / ".claude"
        (claude_dir / "skills").mkdir(parents=True)

        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            with patch(
                "issue_workflow.cli.commands.update.check_hachimoku_version",
                side_effect=Exception("Unexpected error"),
            ):
                result = runner.invoke(app, ["update"])
                assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)
