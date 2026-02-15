"""Integration tests for create-pr subcommand."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from tests.conftest import make_claude_result

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.create_pr"


class TestCreatePrCliExecution:
    """CliRunner E2E tests for create-pr."""

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_succeeds(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """issue-workflow create-pr succeeds."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["create-pr"])

        assert result.exit_code == 0

    def test_help_shows_security_notice(self) -> None:
        """--help output contains security notice."""
        result = runner.invoke(app, ["create-pr", "--help"])

        assert result.exit_code == 0
        assert "dangerously-skip-permissions" in result.output

    def test_help_shows_usage(self) -> None:
        """--help output shows usage information."""
        result = runner.invoke(app, ["create-pr", "--help"])

        assert result.exit_code == 0
        assert "create-pr" in result.output

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

        result = runner.invoke(app, ["create-pr", "-v"])

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

        result = runner.invoke(app, ["create-pr", "--timeout", "600"])

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
        """Output contains [create-pr] Starting... message."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["create-pr"])

        assert "[create-pr] Starting" in result.output

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Output contains [create-pr] Done. message."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["create-pr"])

        assert "[create-pr] Done." in result.output

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

        result = runner.invoke(app, ["create-pr"])

        assert result.exit_code == 1
