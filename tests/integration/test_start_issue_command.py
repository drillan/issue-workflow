"""Integration tests for start-issue subcommand."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.start_issue"


class TestStartIssueCliExecution:
    """CliRunner E2E tests for start-issue."""

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_succeeds(
        self,
        mock_deps: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """issue-workflow start-issue 199 succeeds."""
        result = runner.invoke(app, ["start-issue", "199"])

        assert result.exit_code == 0

    def test_requires_issue_number(self) -> None:
        """start-issue without issue_number shows error."""
        result = runner.invoke(app, ["start-issue"])

        assert result.exit_code != 0

    def test_rejects_non_integer_issue_number(self) -> None:
        """start-issue with non-integer issue_number shows error."""
        result = runner.invoke(app, ["start-issue", "abc"])

        assert result.exit_code != 0

    def test_help_shows_security_notice(self) -> None:
        """--help output contains security notice about --dangerously-skip-permissions."""
        result = runner.invoke(app, ["start-issue", "--help"])

        assert result.exit_code == 0
        assert "dangerously-skip-permissions" in result.output

    def test_help_shows_usage(self) -> None:
        """--help output shows usage information."""
        result = runner.invoke(app, ["start-issue", "--help"])

        assert result.exit_code == 0
        assert "ISSUE_NUMBER" in result.output

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.check_dependencies")
    def test_verbose_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """-v option is accepted."""
        result = runner.invoke(app, ["start-issue", "199", "-v"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.check_dependencies")
    def test_timeout_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """--timeout option is accepted."""
        result = runner.invoke(app, ["start-issue", "199", "--timeout", "600"])

        assert result.exit_code == 0

    @patch(f"{_MOD}._prepare_worktree", return_value=Path("/tmp/mock-worktree"))
    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.check_dependencies")
    def test_worktree_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_skill: MagicMock,
        mock_prepare_wt: MagicMock,
    ) -> None:
        """--worktree option is accepted."""
        result = runner.invoke(app, ["start-issue", "199", "--worktree"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.run_claude_skill", return_value=1)
    @patch(f"{_MOD}.check_dependencies")
    def test_nonzero_exit_code_propagated(
        self,
        mock_deps: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """Non-zero exit code from run_claude_skill is propagated."""
        result = runner.invoke(app, ["start-issue", "199"])

        assert result.exit_code == 1
