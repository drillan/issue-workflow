"""Integration tests for start-issue subcommand."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from issue_workflow.models.claude_result import ClaudeResult

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.start_issue"


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


def _patch_all() -> tuple[MagicMock, MagicMock, MagicMock]:
    """Create standard mocks for all external dependencies."""
    mock_deps = MagicMock()
    mock_runner_instance = MagicMock()
    mock_runner_instance.run.return_value = _make_claude_result()
    mock_logger_instance = MagicMock()
    return mock_deps, mock_runner_instance, mock_logger_instance


class TestStartIssueCliExecution:
    """CliRunner E2E tests for start-issue."""

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_succeeds(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """issue-workflow start-issue 199 succeeds."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

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

        result = runner.invoke(app, ["start-issue", "199", "-v"])

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

        result = runner.invoke(app, ["start-issue", "199", "--timeout", "600"])

        assert result.exit_code == 0

    @patch(f"{_MOD}._prepare_worktree", return_value=Path("/tmp/mock-worktree"))
    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_worktree_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
        mock_prepare_wt: MagicMock,
    ) -> None:
        """--worktree option is accepted."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["start-issue", "199", "--worktree"])

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
        """Output contains [start-issue] Starting... message."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["start-issue", "199"])

        assert "[start-issue] Starting" in result.output

    @patch(f"{_MOD}.ExecutionLogger")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner_cls: MagicMock,
        mock_logger_cls: MagicMock,
    ) -> None:
        """Output contains [start-issue] Done. message."""
        mock_runner_cls.return_value.run.return_value = _make_claude_result()

        result = runner.invoke(app, ["start-issue", "199"])

        assert "[start-issue] Done." in result.output

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

        result = runner.invoke(app, ["start-issue", "199"])

        assert result.exit_code == 1
