"""Integration tests for GitHub service."""

from unittest.mock import MagicMock, patch

from issue_workflow.services.github import (
    check_gh_availability,
    get_issue,
    get_pr,
)


class TestGhAvailability:
    """Tests for gh CLI availability check."""

    def test_gh_available_and_authenticated(self) -> None:
        """Test when gh is available and authenticated."""
        with patch("subprocess.run") as mock_run:
            # Mock successful version check
            mock_version = MagicMock()
            mock_version.returncode = 0

            # Mock successful auth check
            mock_auth = MagicMock()
            mock_auth.returncode = 0

            mock_run.side_effect = [mock_version, mock_auth]

            available, message = check_gh_availability()
            assert available is True
            assert "available" in message.lower()

    def test_gh_not_installed(self) -> None:
        """Test when gh is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            available, message = check_gh_availability()
            assert available is False
            assert "not found" in message.lower()

    def test_gh_not_authenticated(self) -> None:
        """Test when gh is installed but not authenticated."""
        with patch("subprocess.run") as mock_run:
            # Mock successful version check
            mock_version = MagicMock()
            mock_version.returncode = 0

            # Mock failed auth check
            mock_auth = MagicMock()
            mock_auth.returncode = 1

            mock_run.side_effect = [mock_version, mock_auth]

            available, message = check_gh_availability()
            assert available is False
            assert "auth" in message.lower()


class TestGetIssue:
    """Tests for get_issue function."""

    def test_get_issue_success(self) -> None:
        """Test successful issue fetch."""
        mock_output = """
        {
            "number": 123,
            "title": "Test Issue",
            "body": "Test body",
            "labels": [{"name": "bug"}],
            "state": "OPEN"
        }
        """
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result

            result = get_issue(123)
            assert result.success is True
            assert result.data is not None
            assert isinstance(result.data, dict)
            assert result.data["number"] == 123

    def test_get_issue_not_found(self) -> None:
        """Test issue not found."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Could not resolve to an Issue with the number of 999"
            mock_run.return_value = mock_result

            result = get_issue(999)
            assert result.success is False
            assert result.error is not None


class TestGetPr:
    """Tests for get_pr function."""

    def test_get_pr_success(self) -> None:
        """Test successful PR fetch."""
        mock_output = """
        {
            "number": 100,
            "title": "Test PR",
            "state": "OPEN",
            "mergeable": "MERGEABLE",
            "baseRefName": "main",
            "headRefName": "feat/123-test"
        }
        """
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result

            result = get_pr(100)
            assert result.success is True
            assert result.data is not None
            assert isinstance(result.data, dict)
            assert result.data["number"] == 100

    def test_get_pr_not_found(self) -> None:
        """Test PR not found."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Could not resolve to a PullRequest"
            mock_run.return_value = mock_result

            result = get_pr(999)
            assert result.success is False
            assert result.error is not None
