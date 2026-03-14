"""Integration tests for run subcommand."""

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from tests.conftest import make_claude_result

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.run"


@contextmanager
def _patch_all_success() -> Iterator[None]:
    """Patch all external calls for a successful full workflow run."""
    mock_instance = MagicMock()
    mock_instance.run.return_value = make_claude_result()

    with (
        patch(f"{_MOD}.check_dependencies"),
        patch(f"{_MOD}.ClaudeRunner", return_value=mock_instance),
        patch(f"{_MOD}.log_execution"),
        patch(f"{_MOD}.detect_pr_number", return_value=300),
        patch(
            f"{_MOD}.subprocess.run",
            return_value=MagicMock(returncode=0, stdout="", stderr=""),
        ),
    ):
        yield


class TestRunCliExecution:
    """CliRunner E2E tests for run subcommand."""

    def test_basic_execution_succeeds(self) -> None:
        """issue-workflow run 199 succeeds with all mocks."""
        with _patch_all_success():
            result = runner.invoke(app, ["run", "199"])

            assert result.exit_code == 0

    def test_requires_issue_number(self) -> None:
        """issue-workflow run (no args) fails."""
        result = runner.invoke(app, ["run"])

        assert result.exit_code != 0

    def test_help_shows_security_notice(self) -> None:
        """--help output contains security notice about --dangerously-skip-permissions."""
        result = runner.invoke(app, ["run", "--help"])

        assert result.exit_code == 0
        assert "dangerously-skip-permissions" in result.output

    def test_help_shows_usage(self) -> None:
        """--help output shows ISSUES argument."""
        result = runner.invoke(app, ["run", "--help"])

        assert result.exit_code == 0
        assert "ISSUES" in result.output

    def test_multi_issue_range_accepted(self) -> None:
        """Range format like '30-32' is accepted."""
        with _patch_all_success():
            result = runner.invoke(app, ["run", "30-32"])

            assert result.exit_code == 0

    def test_invalid_issue_format_fails(self) -> None:
        """Invalid issue format returns non-zero exit code."""
        result = runner.invoke(app, ["run", "abc"])

        assert result.exit_code != 0

    def test_verbose_option_accepted(self) -> None:
        """-v option is accepted."""
        with _patch_all_success():
            result = runner.invoke(app, ["run", "199", "-v"])

            assert result.exit_code == 0

    def test_timeout_option_accepted(self) -> None:
        """--timeout option is accepted."""
        with _patch_all_success():
            result = runner.invoke(app, ["run", "199", "--timeout", "600"])

            assert result.exit_code == 0

    def test_worktree_option_accepted(self) -> None:
        """--worktree option is accepted."""
        with (
            _patch_all_success(),
            patch(f"{_MOD}._prepare_worktree", return_value=None),
        ):
            # worktree_failure returns 1 but the option itself is accepted
            result = runner.invoke(app, ["run", "199", "--worktree"])

            # Even if worktree fails, the option was accepted (no parse error)
            assert "Error" not in result.output or result.exit_code == 1

    def test_nonzero_exit_code_propagated(self) -> None:
        """Non-zero exit code from step failure is propagated."""
        mock_instance = MagicMock()
        mock_instance.run.return_value = make_claude_result(exit_code=1, is_error=True)

        with (
            patch(f"{_MOD}.check_dependencies"),
            patch(f"{_MOD}.ClaudeRunner", return_value=mock_instance),
            patch(f"{_MOD}.log_execution"),
            patch(f"{_MOD}.detect_pr_number", return_value=300),
            patch(
                f"{_MOD}.subprocess.run",
                return_value=MagicMock(returncode=0, stdout="", stderr=""),
            ),
        ):
            result = runner.invoke(app, ["run", "199"])

            assert result.exit_code == 1

    def test_output_contains_step_messages(self) -> None:
        """Output contains step starting/done messages."""
        with _patch_all_success():
            result = runner.invoke(app, ["run", "199"])

            assert "start-issue" in result.output
            assert "create-pr" in result.output
            assert "merge-pr" in result.output
