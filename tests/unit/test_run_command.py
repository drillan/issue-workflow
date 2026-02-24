"""Unit tests for run subcommand."""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    HACHIMOKU_DEPENDENCY,
)
from tests.conftest import make_claude_result

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.run"


@pytest.fixture()
def mock_deps() -> Iterator[MagicMock]:
    """Mock check_dependencies to do nothing."""
    with patch(f"{_MOD}.check_dependencies") as m:
        yield m


@pytest.fixture()
def mock_runner() -> Iterator[MagicMock]:
    """Mock ClaudeRunner class; instance.run returns success result."""
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


@pytest.fixture()
def mock_pr_detector() -> Iterator[MagicMock]:
    """Mock detect_pr_number to return 300."""
    with patch(f"{_MOD}.detect_pr_number", return_value=300) as m:
        yield m


@pytest.fixture()
def mock_subprocess() -> Iterator[MagicMock]:
    """Mock subprocess.run for 8moku execution (returncode=0)."""
    with patch(f"{_MOD}.subprocess.run") as m:
        m.return_value = MagicMock(returncode=0)
        yield m


@pytest.fixture()
def mock_prepare_worktree() -> Iterator[MagicMock]:
    """Mock _prepare_worktree to return a worktree path."""
    with patch(f"{_MOD}._prepare_worktree", return_value=Path("/tmp/wt")) as m:
        yield m


@pytest.fixture()
def all_mocks(
    mock_deps: MagicMock,
    mock_runner: MagicMock,
    mock_log_execution: MagicMock,
    mock_pr_detector: MagicMock,
    mock_subprocess: MagicMock,
) -> None:
    """Activate all standard mocks for a successful run."""


class TestRunBasic:
    """Basic behavior tests for full workflow execution."""

    def test_calls_check_dependencies_with_all_three(
        self,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """check_dependencies is called with claude, gh, and 8moku."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.run import _run_workflow

            _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg
            assert HACHIMOKU_DEPENDENCY in deps_arg

    def test_step1_calls_start_issue_prompt(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Step 1 calls ClaudeRunner.run with /start-issue prompt."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        first_call = mock_runner.run.call_args_list[0]
        assert first_call[0][0] == "/start-issue 199 --force"

    def test_step2_calls_create_pr_prompt(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Step 2 calls ClaudeRunner.run with /commit-push-pr prompt."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        second_call = mock_runner.run.call_args_list[1]
        assert second_call[0][0] == "/commit-push-pr"

    def test_step2_calls_detect_pr_number_with_cwd(
        self,
        all_mocks: None,
        mock_pr_detector: MagicMock,
    ) -> None:
        """detect_pr_number is called with cwd=None (no worktree)."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_pr_detector.assert_called_once_with(cwd=None)

    def test_step3a_calls_8moku_subprocess(
        self,
        all_mocks: None,
        mock_subprocess: MagicMock,
    ) -> None:
        """Step 3a calls subprocess.run with 8moku and PR number."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert call_args == ["8moku", "300"]

    def test_step3a_does_not_capture_output(
        self,
        all_mocks: None,
        mock_subprocess: MagicMock,
    ) -> None:
        """8moku subprocess.run must NOT use capture_output so output streams in real-time."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_subprocess.assert_called_once()
        call_kwargs = mock_subprocess.call_args.kwargs
        assert "capture_output" not in call_kwargs
        assert "text" not in call_kwargs
        assert "stdout" not in call_kwargs
        assert "stderr" not in call_kwargs

    def test_step3b_calls_respond_review_prompt(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Step 3b calls ClaudeRunner.run with /respond-review prompt."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        third_call = mock_runner.run.call_args_list[2]
        assert third_call[0][0] == "/respond-review 300"

    def test_step3c_calls_push_changes_prompt(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Step 3c calls ClaudeRunner.run with push-changes prompt."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        fourth_call = mock_runner.run.call_args_list[3]
        assert "/commit-push-pr" in fourth_call[0][0]

    def test_step4_calls_merge_pr_prompt(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Step 4 calls ClaudeRunner.run with /merge-pr prompt."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        fifth_call = mock_runner.run.call_args_list[4]
        assert fifth_call[0][0] == "/merge-pr 300"

    def test_returns_zero_on_all_success(
        self,
        all_mocks: None,
    ) -> None:
        """Returns exit_code=0 when all steps succeed."""
        from issue_workflow.cli.commands.run import _run_workflow

        exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 0

    def test_calls_log_execution_for_each_claude_step(
        self,
        all_mocks: None,
        mock_log_execution: MagicMock,
    ) -> None:
        """log_execution is called 5 times (one per Claude step)."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        # 5 Claude steps: start-issue, create-pr, review-pr, push-changes, merge-pr
        assert mock_log_execution.call_count == 5

    def test_log_execution_receives_correct_command_names(
        self,
        all_mocks: None,
        mock_log_execution: MagicMock,
    ) -> None:
        """log_execution is called with correct command names."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        command_names = [call[0][0] for call in mock_log_execution.call_args_list]
        assert command_names == [
            "start-issue",
            "create-pr",
            "review-pr",
            "push-changes",
            "merge-pr",
        ]


class TestRunStepFailure:
    """Tests for step failure handling."""

    def test_step1_failure_stops_workflow(
        self,
        mock_deps: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Step 1 failure prevents subsequent steps from executing."""
        with patch(f"{_MOD}.ClaudeRunner") as cls:
            instance = MagicMock()
            instance.run.return_value = make_claude_result(exit_code=1, is_error=True)
            cls.return_value = instance

            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 1
            # Only 1 Claude call (start-issue)
            assert instance.run.call_count == 1
            mock_pr_detector.assert_not_called()
            mock_subprocess.assert_not_called()

    def test_step2_failure_stops_before_detect_pr(
        self,
        mock_deps: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Step 2 failure prevents detect_pr_number from being called."""
        with patch(f"{_MOD}.ClaudeRunner") as cls:
            instance = MagicMock()
            # Step 1 succeeds, step 2 fails
            instance.run.side_effect = [
                make_claude_result(exit_code=0),
                make_claude_result(exit_code=1, is_error=True),
            ]
            cls.return_value = instance

            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 1
            assert instance.run.call_count == 2
            mock_pr_detector.assert_not_called()

    def test_detect_pr_exit_propagates_through_workflow(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """typer.Exit from detect_pr_number propagates through _run_workflow."""
        import typer

        with patch(f"{_MOD}.detect_pr_number", side_effect=typer.Exit(code=1)):
            from issue_workflow.cli.commands.run import _run_workflow

            with pytest.raises(typer.Exit) as exc_info:
                _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exc_info.value.exit_code == 1
            # 2 Claude calls (start-issue, create-pr) before detect_pr_number failure
            assert mock_runner.run.call_count == 2
            mock_subprocess.assert_not_called()

    def test_step3a_timeout_stops_workflow(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """8moku subprocess.TimeoutExpired is caught and returns 1."""
        import subprocess as sp

        with patch(
            f"{_MOD}.subprocess.run", side_effect=sp.TimeoutExpired(cmd="8moku", timeout=600)
        ):
            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=600)

            assert exit_code == 1
            # 2 Claude calls before 8moku timeout
            assert mock_runner.run.call_count == 2

    def test_step3a_findings_continues_to_respond(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """8moku non-zero exit code (findings) continues to respond-review."""
        with patch(f"{_MOD}.subprocess.run") as mock_sub:
            mock_sub.return_value = MagicMock(returncode=2)

            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 0
            # 5 Claude calls: start-issue, create-pr, respond-review, push-changes, merge-pr
            assert mock_runner.run.call_count == 5

    def test_step3b_failure_stops_before_push(
        self,
        mock_deps: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """respond-review failure prevents push-changes and merge-pr."""
        with patch(f"{_MOD}.ClaudeRunner") as cls:
            instance = MagicMock()
            # Step 1 ok, step 2 ok, step 3b (respond) fails
            instance.run.side_effect = [
                make_claude_result(exit_code=0),  # start-issue
                make_claude_result(exit_code=0),  # create-pr
                make_claude_result(exit_code=1, is_error=True),  # respond-review
            ]
            cls.return_value = instance

            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 1
            assert instance.run.call_count == 3

    def test_step3c_failure_stops_before_merge(
        self,
        mock_deps: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """push-changes failure prevents merge-pr."""
        with patch(f"{_MOD}.ClaudeRunner") as cls:
            instance = MagicMock()
            instance.run.side_effect = [
                make_claude_result(exit_code=0),  # start-issue
                make_claude_result(exit_code=0),  # create-pr
                make_claude_result(exit_code=0),  # respond-review
                make_claude_result(exit_code=1, is_error=True),  # push-changes
            ]
            cls.return_value = instance

            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 1
            assert instance.run.call_count == 4


class TestRunWorktree:
    """Tests for worktree option."""

    def test_worktree_calls_prepare_worktree(
        self,
        all_mocks: None,
        mock_prepare_worktree: MagicMock,
    ) -> None:
        """--worktree calls _prepare_worktree with issue_number."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=True, verbose=False, timeout=3600)

        mock_prepare_worktree.assert_called_once_with(199)

    def test_worktree_sets_cwd_for_skill_steps(
        self,
        all_mocks: None,
        mock_prepare_worktree: MagicMock,
        mock_runner: MagicMock,
    ) -> None:
        """Skill steps use worktree_path as cwd."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=True, verbose=False, timeout=3600)

        # Steps 1-3 should have cwd=Path("/tmp/wt")
        for call in mock_runner.run.call_args_list[:4]:  # start-issue..push-changes
            assert call.kwargs.get("cwd") == Path("/tmp/wt")

    def test_worktree_sets_cwd_none_for_merge(
        self,
        all_mocks: None,
        mock_prepare_worktree: MagicMock,
        mock_runner: MagicMock,
    ) -> None:
        """merge-pr step uses cwd=None (main repo)."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=True, verbose=False, timeout=3600)

        # Last call (merge-pr) should have cwd=None
        last_call = mock_runner.run.call_args_list[-1]
        assert last_call.kwargs.get("cwd") is None

    def test_worktree_failure_returns_1(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Returns 1 when _prepare_worktree returns None."""
        with patch(f"{_MOD}._prepare_worktree", return_value=None):
            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=True, verbose=False, timeout=3600)

            assert exit_code == 1
            mock_runner.run.assert_not_called()

    def test_no_worktree_cwd_is_none(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Without --worktree, all steps use cwd=None."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

        for call in mock_runner.run.call_args_list:
            assert call.kwargs.get("cwd") is None

    def test_detect_pr_called_with_worktree_cwd(
        self,
        all_mocks: None,
        mock_prepare_worktree: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """detect_pr_number is called with cwd=worktree_path when --worktree."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=True, verbose=False, timeout=3600)

        mock_pr_detector.assert_called_once_with(cwd=Path("/tmp/wt"))


class TestRunKeyboardInterrupt:
    """Tests for KeyboardInterrupt (Ctrl+C) during workflow."""

    def test_keyboard_interrupt_during_claude_step_returns_1(
        self,
        mock_deps: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """KeyboardInterrupt during ClaudeRunner.run causes _run_workflow to return 1."""
        with patch(f"{_MOD}.ClaudeRunner") as cls:
            instance = MagicMock()
            instance.run.side_effect = KeyboardInterrupt()
            cls.return_value = instance

            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 1

    def test_keyboard_interrupt_during_8moku_returns_1(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_log_execution: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """KeyboardInterrupt during 8moku subprocess causes _run_workflow to return 1."""
        with patch(f"{_MOD}.subprocess.run", side_effect=KeyboardInterrupt()):
            from issue_workflow.cli.commands.run import _run_workflow

            exit_code = _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=3600)

            assert exit_code == 1


class TestRunVerbose:
    """Verbose mode tests."""

    def test_verbose_forwarded_to_runner(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=True, timeout=3600)

        for call in mock_runner.run.call_args_list:
            assert call.kwargs.get("verbose") is True


class TestRunTimeout:
    """Timeout option tests."""

    def test_custom_timeout_forwarded(
        self,
        all_mocks: None,
        mock_runner: MagicMock,
    ) -> None:
        """Custom timeout is forwarded to all ClaudeRunner.run calls."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=600)

        for call in mock_runner.run.call_args_list:
            assert call.kwargs.get("timeout_seconds") == 600

    def test_custom_timeout_forwarded_to_8moku(
        self,
        all_mocks: None,
        mock_subprocess: MagicMock,
    ) -> None:
        """Custom timeout is forwarded to 8moku subprocess.run."""
        from issue_workflow.cli.commands.run import _run_workflow

        _run_workflow(issue_number=199, worktree=False, verbose=False, timeout=600)

        mock_subprocess.assert_called_once()
        assert mock_subprocess.call_args.kwargs.get("timeout") == 600
