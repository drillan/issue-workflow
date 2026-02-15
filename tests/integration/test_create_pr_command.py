"""Integration tests for create-pr subcommand."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from issue_workflow.models.claude_result import ClaudeResult

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.create_pr"


def _make_claude_result(
    exit_code: int = 0,
    is_error: bool = False,
) -> ClaudeResult:
    """Create a ClaudeResult for testing."""
    raw_json = json.dumps({"type": "result", "subtype": "success"})
    return ClaudeResult(
        type="result",
        subtype="success",
        is_error=is_error,
        exit_code=exit_code,
        raw_json=raw_json,
    )


class TestCreatePrCliExecution:
    """CliRunner E2E tests for create-pr."""

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_succeeds(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """issue-workflow create-pr succeeds."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

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

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_verbose_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """-v option is accepted."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["create-pr", "-v"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_timeout_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """--timeout option is accepted."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["create-pr", "--timeout", "600"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """Output contains [create-pr] Starting... message."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["create-pr"])

        assert "[create-pr] Starting" in result.output

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """Output contains [create-pr] Done. message."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["create-pr"])

        assert "[create-pr] Done." in result.output

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_nonzero_exit_code_propagated(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """Non-zero exit code from ClaudeResult is propagated."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result(
            exit_code=1, is_error=True
        )

        result = runner.invoke(app, ["create-pr"])

        assert result.exit_code == 1
