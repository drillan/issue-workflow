"""Unit tests for create-pr subcommand."""

import json
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.models.claude_result import ClaudeResult
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import CLAUDE_DEPENDENCY, GH_DEPENDENCY

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.create_pr"


def _make_claude_result(
    exit_code: int = 0,
    is_error: bool = False,
    raw_json: str = "",
) -> ClaudeResult:
    """Create a ClaudeResult for testing."""
    if not raw_json:
        raw_json = json.dumps({"type": "result", "subtype": "success"})
    return ClaudeResult(
        type="result",
        subtype="success",
        is_error=is_error,
        exit_code=exit_code,
        raw_json=raw_json,
    )


@pytest.fixture()
def mock_deps() -> Iterator[MagicMock]:
    """Mock check_dependencies to do nothing."""
    with patch(f"{_MOD}.check_dependencies") as m:
        yield m


@pytest.fixture()
def mock_runner() -> Iterator[MagicMock]:
    """Mock ClaudeRunner with a successful result."""
    with patch(f"{_MOD}.ClaudeRunner") as cls:
        instance = MagicMock()
        instance.run.return_value = _make_claude_result()
        cls.return_value = instance
        yield instance


@pytest.fixture()
def mock_logger() -> Iterator[MagicMock]:
    """Mock ExecutionLogger."""
    with patch(f"{_MOD}.ExecutionLogger") as cls:
        instance = MagicMock()
        cls.return_value = instance
        yield instance


class TestCreatePrBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude_only(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Dependency check includes only CLAUDE_DEPENDENCY."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY not in deps_arg

    def test_calls_claude_runner_with_commit_push_pr_prompt(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ClaudeRunner.run is called with '/commit-push-pr'."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == "/commit-push-pr"

    def test_calls_execution_logger(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLogger.log is called."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_logger.log.assert_called_once()

    def test_returns_zero_exit_code_on_success(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Returns exit_code=0 when ClaudeResult.exit_code=0."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        exit_code = _run_create_pr(verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Returns exit_code=1 when ClaudeResult.exit_code=1."""
        mock_runner.run.return_value = _make_claude_result(exit_code=1, is_error=True)

        from issue_workflow.cli.commands.create_pr import _run_create_pr

        exit_code = _run_create_pr(verbose=False, timeout=3600)

        assert exit_code == 1

    def test_cwd_is_none(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """cwd is None (current directory)."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("cwd") is None

    def test_console_output_starting_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Output contains '[create-pr] Starting...'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.create_pr import _run_create_pr

            _run_create_pr(verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[create-pr] Starting" in c for c in all_calls)

    def test_console_output_done_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Output contains '[create-pr] Done. (exit_code=0)'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.create_pr import _run_create_pr

            _run_create_pr(verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[create-pr] Done" in c and "exit_code=0" in c for c in all_calls)


class TestCreatePrErrorHandling:
    """Error handling tests."""

    def test_logger_io_error_continues_with_correct_exit_code(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """OSError in ExecutionLogger.log() prints warning but returns correct exit code."""
        mock_logger.log.side_effect = OSError("Permission denied")

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.create_pr import _run_create_pr

            exit_code = _run_create_pr(verbose=False, timeout=3600)

            assert exit_code == 0
            warning_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("log" in c.lower() for c in warning_calls)


class TestCreatePrVerbose:
    """Verbose mode tests."""

    def test_verbose_passes_verbose_to_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    def test_verbose_starting_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Verbose mode shows '(verbose mode)' in starting message."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.create_pr import _run_create_pr

            _run_create_pr(verbose=True, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("verbose mode" in c for c in all_calls)


class TestCreatePrTimeout:
    """Timeout option tests."""

    def test_custom_timeout_passed_to_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Custom timeout value is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    def test_default_timeout_is_3600(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=DEFAULT_TIMEOUT_SECONDS)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 3600


class TestCreatePrLogEntry:
    """Log entry content tests."""

    def test_log_entry_command_name(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.command is 'create-pr'."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.command == "create-pr"

    def test_log_entry_args_empty(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.args is empty dict."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.args == {}

    def test_log_entry_exit_code(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.exit_code matches ClaudeResult.exit_code."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.exit_code == 0
