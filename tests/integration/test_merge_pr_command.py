"""Integration tests for merge-pr subcommand."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from issue_workflow.cli.main import app

runner = CliRunner()

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.merge_pr"


class TestMergePrCliExecution:
    """CliRunner E2E tests for merge-pr."""

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_basic_execution_with_pr_number(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """issue-workflow merge-pr 300 succeeds."""
        result = runner.invoke(app, ["merge-pr", "300"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_execution_without_pr_number(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """issue-workflow merge-pr (no PR number) uses detect_pr_number."""
        result = runner.invoke(app, ["merge-pr"])

        assert result.exit_code == 0
        mock_detect.assert_called_once()

    def test_help_shows_security_notice(self) -> None:
        """--help output contains security notice about --dangerously-skip-permissions."""
        result = runner.invoke(app, ["merge-pr", "--help"])

        assert result.exit_code == 0
        assert "dangerously-skip-permissions" in result.output

    def test_help_shows_usage(self) -> None:
        """--help output shows usage information."""
        result = runner.invoke(app, ["merge-pr", "--help"])

        assert result.exit_code == 0
        assert "merge-pr" in result.output

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_verbose_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """-v option is accepted."""
        result = runner.invoke(app, ["merge-pr", "300", "-v"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.run_claude_skill", return_value=0)
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_timeout_option_accepted(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """--timeout option is accepted."""
        result = runner.invoke(app, ["merge-pr", "300", "--timeout", "600"])

        assert result.exit_code == 0

    @patch(f"{_MOD}.run_claude_skill", return_value=1)
    @patch(f"{_MOD}.detect_pr_number", return_value=300)
    @patch(f"{_MOD}.check_dependencies")
    def test_nonzero_exit_code_propagated(
        self,
        mock_deps: MagicMock,
        mock_detect: MagicMock,
        mock_skill: MagicMock,
    ) -> None:
        """Non-zero exit code from run_claude_skill is propagated."""
        result = runner.invoke(app, ["merge-pr", "300"])

        assert result.exit_code == 1
