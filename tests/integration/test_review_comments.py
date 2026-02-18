"""Integration tests for PR comment fetching."""

import subprocess
from unittest.mock import MagicMock, patch

from issue_workflow.services.github import get_pr_comments, get_pr_for_branch


class TestGetPrComments:
    """Tests for fetching PR review comments."""

    def test_get_pr_comments_success(self) -> None:
        """Test successful PR comment fetch."""
        mock_output = """
        [
            {
                "id": 1,
                "body": "Please fix this",
                "path": "src/auth.py",
                "line": 10,
                "user": {"login": "reviewer"}
            },
            {
                "id": 2,
                "body": "Good approach",
                "path": "src/auth.py",
                "line": 20,
                "user": {"login": "reviewer"}
            }
        ]
        """
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result

            result = get_pr_comments(100)
            assert result.success is True
            assert result.data is not None
            assert isinstance(result.data, list)
            assert len(result.data) == 2

    def test_get_pr_comments_empty(self) -> None:
        """Test PR with no comments."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "[]"
            mock_run.return_value = mock_result

            result = get_pr_comments(100)
            assert result.success is True
            assert result.data == []

    def test_get_pr_comments_not_found(self) -> None:
        """Test PR not found."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Could not resolve to a PullRequest"
            mock_run.return_value = mock_result

            result = get_pr_comments(999)
            assert result.success is False


class TestGetPrForBranch:
    """Tests for finding PR by branch name."""

    def test_get_pr_for_branch_found(self) -> None:
        """Test finding PR for branch."""
        mock_output = """
        [
            {
                "number": 100,
                "title": "Feature PR",
                "state": "OPEN",
                "mergeable": "MERGEABLE",
                "baseRefName": "main",
                "headRefName": "feat/123-feature"
            }
        ]
        """
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result

            result = get_pr_for_branch("feat/123-feature")
            assert result.success is True
            assert result.data is not None
            assert isinstance(result.data, dict)
            assert result.data["number"] == 100

    def test_get_pr_for_branch_not_found(self) -> None:
        """Test no PR for branch."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "[]"
            mock_run.return_value = mock_result

            result = get_pr_for_branch("feat/unknown")
            assert result.success is False
            assert "No PR found" in (result.error or "")

    def test_get_pr_for_branch_filters_open_state(self) -> None:
        """Test that gh pr list is called with --state open and correct --head branch."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "[]"
            mock_run.return_value = mock_result

            get_pr_for_branch("feat/123-feature")

            call_args = mock_run.call_args[0][0]
            assert "--state" in call_args
            state_idx = call_args.index("--state")
            assert call_args[state_idx + 1] == "open"
            assert "--head" in call_args
            head_idx = call_args.index("--head")
            assert call_args[head_idx + 1] == "feat/123-feature"

    def test_get_pr_for_branch_subprocess_failure(self) -> None:
        """Test error handling when gh command fails (e.g., network error)."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "HTTP 502: Bad Gateway"
            mock_run.return_value = mock_result

            result = get_pr_for_branch("feat/123-feature")
            assert result.success is False
            assert result.error is not None
            assert "HTTP 502" in result.error

    def test_get_pr_for_branch_invalid_json_response(self) -> None:
        """Test error handling when gh returns invalid JSON."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "not valid json{{"
            mock_run.return_value = mock_result

            result = get_pr_for_branch("feat/123-feature")
            assert result.success is False
            assert result.error is not None
            assert "Invalid JSON response" in result.error

    def test_get_pr_for_branch_subprocess_exception(self) -> None:
        """Test error handling when subprocess.run raises SubprocessError."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("command not found")

            result = get_pr_for_branch("feat/123-feature")
            assert result.success is False
            assert result.error is not None
            assert "command not found" in result.error
