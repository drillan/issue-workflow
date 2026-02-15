"""Unit tests for push-changes subcommand."""

import json
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.models.claude_result import ClaudeResult
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    HACHIMOKU_DEPENDENCY,
)

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.push_changes"


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
        instance.log.return_value = Path("/tmp/test.jsonl")
        cls.return_value = instance
        yield instance


@pytest.fixture()
def mock_pr_detector() -> Iterator[MagicMock]:
    """Mock detect_pr_number to return 300."""
    with patch(f"{_MOD}.detect_pr_number", return_value=300) as m:
        yield m


class TestPushChangesBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude_and_gh(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Dependency check includes CLAUDE_DEPENDENCY and GH_DEPENDENCY."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY in deps_arg

    def test_does_not_require_hachimoku(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Dependency check does not include HACHIMOKU_DEPENDENCY."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        deps_arg = mock_deps.call_args[0][0]
        assert HACHIMOKU_DEPENDENCY not in deps_arg

    def test_calls_detect_pr_number(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """detect_pr_number is called for auto-detection (FR-015a)."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        mock_pr_detector.assert_called_once()

    def test_calls_claude_runner_with_push_prompt(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """ClaudeRunner.run is called with prompt containing /commit-push-pr."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        prompt = call_args[0][0]
        assert "/commit-push-pr" in prompt

    def test_prompt_contains_pr_skip_instruction(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Prompt contains instruction to skip PR creation."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        call_args = mock_runner.run.call_args
        prompt = call_args[0][0]
        assert "PR" in prompt
        assert "スキップ" in prompt or "skip" in prompt.lower()

    def test_calls_execution_logger(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """ExecutionLogger.log is called."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        mock_logger.log.assert_called_once()

    def test_returns_zero_exit_code_on_success(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Returns exit_code=0 when ClaudeResult.exit_code=0."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        exit_code = _run_push_changes(verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Returns exit_code=1 when ClaudeResult.exit_code=1."""
        mock_runner.run.return_value = _make_claude_result(exit_code=1, is_error=True)

        from issue_workflow.cli.commands.push_changes import _run_push_changes

        exit_code = _run_push_changes(verbose=False, timeout=3600)

        assert exit_code == 1

    def test_cwd_is_none(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """cwd is None (current directory)."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("cwd") is None

    def test_console_output_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Output contains '[push-changes] Starting...'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.push_changes import _run_push_changes

            _run_push_changes(verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[push-changes] Starting" in c for c in all_calls)

    def test_console_output_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Output contains '[push-changes] Done. (exit_code=0)'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.push_changes import _run_push_changes

            _run_push_changes(verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[push-changes] Done" in c and "exit_code=0" in c for c in all_calls)


class TestPushChangesVerbose:
    """Verbose mode tests."""

    def test_verbose_passes_verbose_to_runner(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    def test_verbose_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Verbose mode shows '(verbose mode)' in starting message."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.push_changes import _run_push_changes

            _run_push_changes(verbose=True, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("verbose mode" in c for c in all_calls)

    def test_verbose_passes_on_tool_use_callback(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Verbose mode passes on_tool_use callback to ClaudeRunner.run."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("on_tool_use") is not None


class TestPushChangesTimeout:
    """Timeout option tests."""

    def test_custom_timeout_passed_to_runner(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Custom --timeout value is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    def test_default_timeout_is_3600(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=DEFAULT_TIMEOUT_SECONDS)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 3600


class TestPushChangesLogEntry:
    """Log entry content tests."""

    def test_log_entry_command_name(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """ExecutionLog.command is 'push-changes'."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.command == "push-changes"

    def test_log_entry_args_contain_pr_number(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """ExecutionLog.args contains pr_number for log filename."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.args["pr_number"] == 300

    def test_log_entry_exit_code(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """ExecutionLog.exit_code matches ClaudeResult.exit_code."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.exit_code == 0


class TestPushChangesErrorHandling:
    """Error handling tests."""

    def test_logger_io_error_continues_with_correct_exit_code(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """OSError in ExecutionLogger.log() prints warning but returns correct exit code."""
        mock_logger.log.side_effect = OSError("Permission denied")

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.push_changes import _run_push_changes

            exit_code = _run_push_changes(verbose=False, timeout=3600)

            assert exit_code == 0
            warning_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("log" in c.lower() for c in warning_calls)
