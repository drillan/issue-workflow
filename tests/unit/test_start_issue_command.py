"""Unit tests for start-issue subcommand."""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import CLAUDE_DEPENDENCY, GH_DEPENDENCY
from tests.conftest import make_claude_result

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.start_issue"


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
        instance.run.return_value = make_claude_result()
        cls.return_value = instance
        yield instance


@pytest.fixture()
def mock_log_execution() -> Iterator[MagicMock]:
    """Mock log_execution to do nothing."""
    with patch(f"{_MOD}.log_execution") as m:
        yield m


class TestStartIssueBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Dependency check includes CLAUDE_DEPENDENCY."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY not in deps_arg

    def test_calls_claude_runner_with_correct_prompt(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """ClaudeRunner.run is called with '/start-issue {issue_number}'."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_runner.run.assert_called_once()
        call_kwargs = mock_runner.run.call_args
        assert call_kwargs[0][0] == "/start-issue 199"

    def test_calls_log_execution(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution is called."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_log_execution.assert_called_once()

    def test_returns_zero_exit_code_on_success(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Returns exit_code=0 when ClaudeResult.exit_code=0."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        exit_code = _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Returns exit_code=1 when ClaudeResult.exit_code=1."""
        mock_runner.run.return_value = make_claude_result(exit_code=1, is_error=True)

        from issue_workflow.cli.commands.start_issue import _run_start_issue

        exit_code = _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 1

    def test_console_output_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
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
        mock_log_execution: MagicMock,
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    def test_verbose_starting_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Verbose mode shows '(verbose mode)' in starting message."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("verbose mode" in c for c in all_calls)

    def test_verbose_passes_on_tool_use_callback(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Verbose mode passes on_tool_use callback to ClaudeRunner.run."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("on_tool_use") is not None


class TestStartIssueTimeout:
    """Timeout option tests."""

    def test_custom_timeout_passed_to_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Custom --timeout value is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    def test_default_timeout_is_3600(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Without --worktree, cwd is None (current directory)."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("cwd") is None


class TestStartIssueErrorHandling:
    """Error handling tests."""

    def test_worktree_git_error_shows_message_and_exits(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """GitError in _prepare_worktree prints error and returns 1."""
        from issue_workflow.lib.git import GitError

        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(f"{_MOD}.ui") as mock_ui,
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git.worktree_add.side_effect = GitError("branch already exists")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            exit_code = _run_start_issue(
                issue_number=199, worktree=True, verbose=False, timeout=3600
            )

            assert exit_code == 1
            error_calls = [str(c) for c in mock_ui.print_error.call_args_list]
            assert any("worktree" in c.lower() for c in error_calls)


class TestStartIssueLogArgs:
    """Tests for log_execution call arguments."""

    def test_log_command_name(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution is called with command_name='start-issue'."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert mock_log_execution.call_args[0][0] == "start-issue"

    def test_log_args_contain_issue_number(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution args dict contains issue_number."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert mock_log_execution.call_args[0][1]["issue_number"] == 199

    def test_log_args_contain_worktree_flag(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution args dict contains worktree flag."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert mock_log_execution.call_args[0][1]["worktree"] is False

    def test_log_timeout_passed(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution receives timeout value."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=600)

        assert mock_log_execution.call_args[0][3] == 600
