"""Integration tests for review-pr subcommand."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app
from tests.conftest import make_claude_result

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.review_pr"


class TestReviewPrCliExecution:
    """CliRunner E2E tests for review-pr."""

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_with_pr_number(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """issue-workflow review-pr 300 succeeds."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr", "300"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_execution_without_pr_number(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """issue-workflow review-pr (no PR number) uses detect_pr_number."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr"])

        assert result.exit_code == 0
        mock_detect.assert_called_once()

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_review_only_succeeds(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """issue-workflow review-pr --review-only 300 succeeds."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["review-pr", "300", "--review-only"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_respond_only_succeeds(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """issue-workflow review-pr --respond-only 300 succeeds."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr", "300", "--respond-only"])

        assert result.exit_code == 0

    def test_mutual_exclusion_error(self) -> None:
        """--review-only + --respond-only shows error."""
        result = runner.invoke(app, ["review-pr", "300", "--review-only", "--respond-only"])

        assert result.exit_code == 1

    def test_help_shows_security_notice(self) -> None:
        """--help output contains security notice about --dangerously-skip-permissions."""
        result = runner.invoke(app, ["review-pr", "--help"])

        assert result.exit_code == 0
        assert "dangerously-skip-permissions" in result.output

    def test_help_shows_usage(self) -> None:
        """--help output shows usage information."""
        result = runner.invoke(app, ["review-pr", "--help"])

        assert result.exit_code == 0
        assert "review-pr" in result.output

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_verbose_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """-v option is accepted."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr", "300", "-v"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_timeout_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """--timeout option is accepted."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr", "300", "--timeout", "600"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_starting_message(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Output contains [review-pr] Starting... message."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr", "300"])

        assert "[review-pr] Starting" in result.output

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_output_contains_done_message(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Output contains [review-pr] Done. message."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        result = runner.invoke(app, ["review-pr", "300"])

        assert "[review-pr] Done." in result.output

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_nonzero_exit_code_propagated(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_subprocess: MagicMock,
        mock_runner_cls: MagicMock,
        mock_log: MagicMock,
    ) -> None:
        """Non-zero exit code from ClaudeResult is propagated."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_runner_cls.return_value.run.return_value = make_claude_result(
            exit_code=1, is_error=True
        )

        result = runner.invoke(app, ["review-pr", "300"])

        assert result.exit_code == 1
