"""Unit tests for create-pr subcommand."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import CLAUDE_DEPENDENCY, GH_DEPENDENCY
from tests.conftest import make_claude_result

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.create_pr"


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


class TestCreatePrBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude_only(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Dependency check includes only CLAUDE_DEPENDENCY."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY not in deps_arg

    def test_calls_claude_runner_with_commit_push_pr_prompt(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """ClaudeRunner.run is called with '/commit-push-pr'."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == "/commit-push-pr"

    def test_calls_log_execution(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution is called."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_log_execution.assert_called_once()

    def test_returns_zero_exit_code_on_success(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Returns exit_code=0 when ClaudeResult.exit_code=0."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        exit_code = _run_create_pr(verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Returns exit_code=1 when ClaudeResult.exit_code=1."""
        mock_runner.run.return_value = make_claude_result(exit_code=1, is_error=True)

        from issue_workflow.cli.commands.create_pr import _run_create_pr

        exit_code = _run_create_pr(verbose=False, timeout=3600)

        assert exit_code == 1

    def test_cwd_is_none(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """cwd is None (current directory)."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("cwd") is None

    def test_console_output_starting_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Output contains '[create-pr] Starting...'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.create_pr import _run_create_pr

            _run_create_pr(verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[create-pr] Starting" in c for c in all_calls)

    def test_console_output_done_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Output contains '[create-pr] Done. (exit_code=0)'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.create_pr import _run_create_pr

            _run_create_pr(verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[create-pr] Done" in c and "exit_code=0" in c for c in all_calls)


class TestCreatePrVerbose:
    """Verbose mode tests."""

    def test_verbose_passes_verbose_to_runner(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=True, timeout=3600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    def test_verbose_starting_message(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
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
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Custom timeout value is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=600)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    def test_default_timeout_is_3600(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=DEFAULT_TIMEOUT_SECONDS)

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 3600


class TestCreatePrLogArgs:
    """Tests for log_execution call arguments."""

    def test_log_command_name(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution is called with command_name='create-pr'."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        assert mock_log_execution.call_args[0][0] == "create-pr"

    def test_log_args_empty(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution args dict is empty."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        assert mock_log_execution.call_args[0][1] == {}

    def test_log_timeout_passed(
        self, mock_deps: MagicMock, mock_runner: MagicMock, mock_log_execution: MagicMock
    ) -> None:
        """log_execution receives timeout value."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=600)

        assert mock_log_execution.call_args[0][3] == 600
