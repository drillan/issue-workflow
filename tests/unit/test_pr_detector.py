"""Unit tests for PR detector service."""

from unittest.mock import MagicMock, patch

import pytest
import typer

from issue_workflow.services.pr_detector import detect_pr_number


class TestDetectPrNumber:
    """Tests for detect_pr_number function."""

    def test_explicit_pr_number_returned_directly(self) -> None:
        """Test explicit pr_number argument is returned as-is."""
        result = detect_pr_number(pr_number=42)
        assert result == 42

    @patch("issue_workflow.services.pr_detector.get_pr_for_branch")
    @patch("issue_workflow.services.pr_detector.GitOperations")
    def test_auto_detect_from_current_branch(
        self, mock_git_ops: MagicMock, mock_get_pr: MagicMock
    ) -> None:
        """Test PR number auto-detected from current branch."""
        mock_instance = MagicMock()
        mock_instance.get_current_branch.return_value = "feat/42-test"
        mock_git_ops.return_value = mock_instance

        mock_get_pr.return_value = MagicMock(success=True, data={"number": 42}, error=None)

        result = detect_pr_number()
        assert result == 42

    @patch("issue_workflow.services.pr_detector.get_pr_for_branch")
    @patch("issue_workflow.services.pr_detector.GitOperations")
    def test_auto_detect_no_pr_found_raises_exit(
        self, mock_git_ops: MagicMock, mock_get_pr: MagicMock
    ) -> None:
        """Test typer.Exit raised when no PR found for branch."""
        mock_instance = MagicMock()
        mock_instance.get_current_branch.return_value = "feat/99-no-pr"
        mock_git_ops.return_value = mock_instance

        mock_get_pr.return_value = MagicMock(
            success=False, data=None, error="No PR found for branch"
        )

        with pytest.raises(typer.Exit):
            detect_pr_number()

    @patch("issue_workflow.services.pr_detector.get_pr_for_branch")
    @patch("issue_workflow.services.pr_detector.GitOperations")
    def test_explicit_takes_priority_over_auto(
        self, mock_git_ops: MagicMock, mock_get_pr: MagicMock
    ) -> None:
        """Test explicit argument takes priority over auto-detection."""
        result = detect_pr_number(pr_number=100)
        assert result == 100
        mock_git_ops.assert_not_called()
        mock_get_pr.assert_not_called()

    @patch("issue_workflow.services.pr_detector.get_pr_for_branch")
    @patch("issue_workflow.services.pr_detector.GitOperations")
    def test_auto_detect_uses_get_pr_for_branch(
        self, mock_git_ops: MagicMock, mock_get_pr: MagicMock
    ) -> None:
        """Test auto-detect calls get_pr_for_branch with branch name."""
        mock_instance = MagicMock()
        mock_instance.get_current_branch.return_value = "feat/55-some-feature"
        mock_git_ops.return_value = mock_instance

        mock_get_pr.return_value = MagicMock(success=True, data={"number": 10}, error=None)

        detect_pr_number()
        mock_get_pr.assert_called_once_with("feat/55-some-feature")
