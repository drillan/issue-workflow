"""Unit tests for review-pr subcommand."""

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
_MOD = "issue_workflow.cli.commands.review_pr"


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


@pytest.fixture()
def mock_subprocess() -> Iterator[MagicMock]:
    """Mock subprocess.run for 8moku execution."""
    with patch(f"{_MOD}.subprocess.run") as m:
        m.return_value = MagicMock(returncode=0)
        yield m


class TestReviewPrBasic:
    """Basic behavior tests for default mode (review + respond)."""

    def test_calls_detect_pr_number(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """detect_pr_number is called with the provided pr_number."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_pr_detector.assert_called_once_with(300)

    def test_runs_8moku_with_pr_number(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """8moku is executed with the detected PR number."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=None,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_subprocess.assert_called_once()
        cmd = mock_subprocess.call_args[0][0]
        assert cmd == ["8moku", "300"]

    def test_calls_claude_runner_with_respond_review_prompt(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """ClaudeRunner.run is called with '/respond-review {pr_number}'."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=None,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == "/respond-review 300"

    def test_calls_execution_logger(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """ExecutionLogger.log is called in default mode."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=None,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_logger.log.assert_called_once()

    def test_returns_zero_exit_code_on_success(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Returns exit_code=0 when both 8moku and claude succeed."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        exit_code = _run_review_pr(
            pr_number=None,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        assert exit_code == 0

    def test_returns_nonzero_when_claude_fails(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Returns nonzero exit_code when ClaudeResult has nonzero exit_code."""
        mock_runner.run.return_value = _make_claude_result(exit_code=1, is_error=True)

        from issue_workflow.cli.commands.review_pr import _run_review_pr

        exit_code = _run_review_pr(
            pr_number=None,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        assert exit_code == 1

    def test_console_output_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Output contains '[review-pr] Starting...'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=None,
                review_only=False,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[review-pr] Starting" in c for c in all_calls)

    def test_console_output_done_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Output contains '[review-pr] Done. (exit_code=0)'."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=None,
                review_only=False,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[review-pr] Done" in c and "exit_code=0" in c for c in all_calls)


class TestReviewPrReviewOnly:
    """Tests for --review-only mode."""

    def test_review_only_runs_8moku(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only executes 8moku."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=True,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_subprocess.assert_called_once()

    def test_review_only_skips_claude(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only does not call ClaudeRunner.run."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=True,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_runner.run.assert_not_called()

    def test_review_only_skips_log(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only does not call ExecutionLogger.log."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=True,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        mock_logger.log.assert_not_called()

    def test_review_only_returns_8moku_exit_code(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only returns 8moku's exit code."""
        mock_subprocess.return_value = MagicMock(returncode=0)

        from issue_workflow.cli.commands.review_pr import _run_review_pr

        exit_code = _run_review_pr(
            pr_number=300,
            review_only=True,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        assert exit_code == 0


class TestReviewPrRespondOnly:
    """Tests for --respond-only mode."""

    def test_respond_only_skips_8moku(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--respond-only does not execute 8moku."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=True,
            verbose=False,
            timeout=3600,
        )

        mock_subprocess.assert_not_called()

    def test_respond_only_runs_claude(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--respond-only calls ClaudeRunner.run."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=True,
            verbose=False,
            timeout=3600,
        )

        mock_runner.run.assert_called_once()

    def test_respond_only_logs_execution(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--respond-only calls ExecutionLogger.log."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=True,
            verbose=False,
            timeout=3600,
        )

        mock_logger.log.assert_called_once()


class TestReviewPrMutualExclusion:
    """Tests for --review-only + --respond-only mutual exclusion."""

    def test_mutual_exclusion_raises_exit(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only + --respond-only raises typer.Exit."""
        import typer

        from issue_workflow.cli.commands.review_pr import _run_review_pr

        with pytest.raises(typer.Exit) as exc_info:
            _run_review_pr(
                pr_number=300,
                review_only=True,
                respond_only=True,
                verbose=False,
                timeout=3600,
            )

        assert exc_info.value.exit_code == 1

    def test_mutual_exclusion_shows_error(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only + --respond-only shows error message."""
        import typer

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            with pytest.raises(typer.Exit):
                _run_review_pr(
                    pr_number=300,
                    review_only=True,
                    respond_only=True,
                    verbose=False,
                    timeout=3600,
                )

            error_calls = [str(c) for c in mock_ui.print_error.call_args_list]
            assert any("review-only" in c and "respond-only" in c for c in error_calls)

    def test_mutual_exclusion_skips_all_execution(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only + --respond-only does not execute anything."""
        import typer

        from issue_workflow.cli.commands.review_pr import _run_review_pr

        with pytest.raises(typer.Exit):
            _run_review_pr(
                pr_number=300,
                review_only=True,
                respond_only=True,
                verbose=False,
                timeout=3600,
            )

        mock_subprocess.assert_not_called()
        mock_runner.run.assert_not_called()


class TestReviewPrDependencies:
    """Tests for conditional dependency checking."""

    def test_default_mode_pr_number_none_requires_all(
        self,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Default mode with pr_number=None requires claude + gh + 8moku."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=None,
                review_only=False,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            deps_arg = mock_deps.call_args[0][0]
            assert HACHIMOKU_DEPENDENCY in deps_arg
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg

    def test_default_mode_pr_explicit_skips_gh(
        self,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Default mode with explicit pr_number does not require gh."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=300,
                review_only=False,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            deps_arg = mock_deps.call_args[0][0]
            assert HACHIMOKU_DEPENDENCY in deps_arg
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY not in deps_arg

    def test_review_only_requires_8moku_only(
        self,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only with explicit PR requires only 8moku."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=300,
                review_only=True,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            deps_arg = mock_deps.call_args[0][0]
            assert HACHIMOKU_DEPENDENCY in deps_arg
            assert CLAUDE_DEPENDENCY not in deps_arg
            assert GH_DEPENDENCY not in deps_arg

    def test_review_only_no_pr_requires_8moku_and_gh(
        self,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--review-only without PR requires 8moku + gh."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=None,
                review_only=True,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            deps_arg = mock_deps.call_args[0][0]
            assert HACHIMOKU_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg
            assert CLAUDE_DEPENDENCY not in deps_arg

    def test_respond_only_requires_claude_only(
        self,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--respond-only with explicit PR requires only claude."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=300,
                review_only=False,
                respond_only=True,
                verbose=False,
                timeout=3600,
            )

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert HACHIMOKU_DEPENDENCY not in deps_arg
            assert GH_DEPENDENCY not in deps_arg

    def test_respond_only_no_pr_requires_claude_and_gh(
        self,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """--respond-only without PR requires claude + gh."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=None,
                review_only=False,
                respond_only=True,
                verbose=False,
                timeout=3600,
            )

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg
            assert HACHIMOKU_DEPENDENCY not in deps_arg


class TestReviewPrVerbose:
    """Verbose mode tests."""

    def test_verbose_passes_verbose_to_runner(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=True,
            timeout=3600,
        )

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    def test_verbose_starting_message(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Verbose mode shows '(verbose mode)' in starting message."""
        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            _run_review_pr(
                pr_number=300,
                review_only=False,
                respond_only=False,
                verbose=True,
                timeout=3600,
            )

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("verbose mode" in c for c in all_calls)

    def test_verbose_passes_on_tool_use_callback(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Verbose mode passes on_tool_use callback to ClaudeRunner.run."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=True,
            timeout=3600,
        )

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("on_tool_use") is not None


class TestReviewPrTimeout:
    """Timeout option tests."""

    def test_custom_timeout_passed_to_runner(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Custom --timeout value is forwarded to ClaudeRunner.run."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=600,
        )

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    def test_default_timeout_is_3600(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        call_kwargs = mock_runner.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 3600


class TestReviewPrLogEntry:
    """Log entry content tests."""

    def test_log_entry_command_name(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """ExecutionLog.command is 'review-pr'."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        entry = mock_logger.log.call_args[0][0]
        assert entry.command == "review-pr"

    def test_log_entry_args_contain_pr_number(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """ExecutionLog.args contains pr_number."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        entry = mock_logger.log.call_args[0][0]
        assert entry.args["pr_number"] == 300

    def test_log_entry_exit_code(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """ExecutionLog.exit_code matches ClaudeResult.exit_code."""
        from issue_workflow.cli.commands.review_pr import _run_review_pr

        _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        entry = mock_logger.log.call_args[0][0]
        assert entry.exit_code == 0


class TestReviewPrErrorHandling:
    """Error handling tests."""

    def test_8moku_failure_stops_execution(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """8moku failure skips respond-review and returns nonzero exit code."""
        mock_subprocess.return_value = MagicMock(returncode=1)

        from issue_workflow.cli.commands.review_pr import _run_review_pr

        exit_code = _run_review_pr(
            pr_number=300,
            review_only=False,
            respond_only=False,
            verbose=False,
            timeout=3600,
        )

        assert exit_code == 1
        mock_runner.run.assert_not_called()

    def test_logger_io_error_continues_with_correct_exit_code(
        self,
        mock_deps: MagicMock,
        mock_runner: MagicMock,
        mock_logger: MagicMock,
        mock_pr_detector: MagicMock,
        mock_subprocess: MagicMock,
    ) -> None:
        """OSError in ExecutionLogger.log() prints warning but returns correct exit code."""
        mock_logger.log.side_effect = OSError("Permission denied")

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands.review_pr import _run_review_pr

            exit_code = _run_review_pr(
                pr_number=300,
                review_only=False,
                respond_only=False,
                verbose=False,
                timeout=3600,
            )

            assert exit_code == 0
            warning_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("log" in c.lower() for c in warning_calls)
