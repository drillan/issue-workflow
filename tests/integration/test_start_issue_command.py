"""Integration tests for start-issue subcommand."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from tests.conftest import make_claude_result

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.start_issue"


class TestStartIssueCliExecution:
    """CliRunner E2E tests for start-issue."""

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_succeeds(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """issue-workflow start-issue 199 succeeds."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

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

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_verbose_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """-v option is accepted."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["start-issue", "199", "-v"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_timeout_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """--timeout option is accepted."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["start-issue", "199", "--timeout", "600"])

        assert result.exit_code == 0

    @patch(f"{_MOD}._prepare_worktree", return_value=Path("/tmp/mock-worktree"))
    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_worktree_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
        mock_prepare_wt: MagicMock,
    ) -> None:
        """--worktree option is accepted."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["start-issue", "199", "--worktree"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Output contains [start-issue] Starting... message."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["start-issue", "199"])

        assert "[start-issue] Starting" in result.output

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Output contains [start-issue] Done. message."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["start-issue", "199"])

        assert "[start-issue] Done." in result.output

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_nonzero_exit_code_propagated(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Non-zero exit code from ClaudeResult is propagated."""
        mock_runner_cls.return_value.run.return_value = make_claude_result(
            exit_code=1, is_error=True
        )

        result = runner.invoke(app, ["start-issue", "199"])

        assert result.exit_code == 1
