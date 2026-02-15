"""Unit tests for start-issue subcommand."""

import json
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.models.claude_result import ClaudeResult
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import CLAUDE_DEPENDENCY, GH_DEPENDENCY

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.start_issue"


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


class TestStartIssueBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Dependency check includes CLAUDE_DEPENDENCY."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY not in deps_arg

    def test_calls_claude_runner_with_correct_prompt(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ClaudeRunner.run is called with '/start-issue {issue_number}'."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_runner.run.assert_called_once()
        call_kwargs = mock_runner.run.call_args
        assert call_kwargs[0][0] == "/start-issue 199"

    def test_calls_execution_logger(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLogger.log is called with an ExecutionLog entry."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_logger.log.assert_called_once()

    def test_returns_zero_exit_code_on_success(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Returns exit_code=0 when ClaudeResult.exit_code=0."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        exit_code = _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Returns exit_code=1 when ClaudeResult.exit_code=1."""
        mock_runner.run.return_value = _make_claude_result(exit_code=1, is_error=True)

        from issue_workflow.cli.commands.start_issue import _run_start_issue

        exit_code = _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 1

    def test_console_output_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Output contains '[start-issue] Starting...'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[start-issue] Starting" in c for c in all_calls)

    def test_console_output_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        """Output contains '[start-issue] Done. (exit_code=0)'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[start-issue] Done" in c and "exit_code=0" in c for c in all_calls)


class TestStartIssueVerbose:
    """Verbose mode tests."""

    def test_verbose_passes_verbose_to_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    def test_verbose_starting_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Verbose mode shows '(verbose mode)' in starting message."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("verbose mode" in c for c in all_calls)

    def test_verbose_passes_on_tool_use_callback(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Verbose mode passes on_tool_use callback to ClaudeRunner.run."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("on_tool_use") is not None


class TestStartIssueTimeout:
    """Timeout option tests."""

    def test_custom_timeout_passed_to_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Custom --timeout value is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    def test_default_timeout_is_3600(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(
            issue_number=199,
            worktree=False,
            verbose=False,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 3600


class TestStartIssueWorktree:
    """Worktree option tests."""

    def test_worktree_adds_gh_dependency(
        self, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """--worktree adds GH_DEPENDENCY to dependency check."""
        with (
            patch(f"{_MOD}.check_dependencies") as mock_deps,
            patch(f"{_MOD}.find_worktree_for_branch", return_value=Path("/tmp/wt")),
        ):
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg

    def test_worktree_detects_existing_worktree(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Existing worktree is detected and used as cwd."""
        existing_path = Path("/tmp/existing-wt")

        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=existing_path),
            patch(f"{_MOD}.GitOperations"),
        ):
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            call_kwargs = mock_runner.run.call_args
            assert call_kwargs.kwargs.get("cwd") == existing_path

    def test_worktree_creates_new_when_not_found(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """New worktree is created when not found."""
        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(f"{_MOD}.copy_hachimoku_to_worktree"),
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            mock_git.worktree_add.assert_called_once()

    def test_worktree_copies_hachimoku(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """copy_hachimoku_to_worktree is called after worktree creation."""
        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(f"{_MOD}.copy_hachimoku_to_worktree") as mock_copy,
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            mock_copy.assert_called_once()

    def test_worktree_sets_cwd_for_claude_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Worktree path is passed as cwd to ClaudeRunner.run."""
        wt_path = Path("/tmp/worktree-199")

        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=wt_path),
            patch(f"{_MOD}.GitOperations"),
        ):
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            call_kwargs = mock_runner.run.call_args
            assert call_kwargs.kwargs.get("cwd") == wt_path

    def test_no_worktree_sets_cwd_none(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Without --worktree, cwd is None (current directory)."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("cwd") is None


class TestStartIssueLogEntry:
    """Log entry content tests."""

    def test_log_entry_command_name(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.command is 'start-issue'."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.command == "start-issue"

    def test_log_entry_args_contain_issue_number(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.args contains issue_number."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.args["issue_number"] == 199

    def test_log_entry_args_contain_worktree_flag(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.args contains worktree flag."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.args["worktree"] is False

    def test_log_entry_exit_code(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.exit_code matches ClaudeResult.exit_code."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.exit_code == 0

    def test_log_entry_result_from_raw_json(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """ExecutionLog.result is parsed from ClaudeResult.raw_json."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.result["type"] == "result"
        assert entry.result["subtype"] == "success"

    def test_log_entry_timeout_result(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Timeout case: ExecutionLog.result contains error info."""
        mock_runner.run.return_value = ClaudeResult(exit_code=-1, is_error=True, raw_json="{}")

        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        entry = mock_logger.log.call_args[0][0]
        assert entry.exit_code == -1
