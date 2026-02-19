"""Integration tests for GitHub service."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.github import (
    GhResult,
    _run_gh,
    check_gh_availability,
    get_issue,
    get_pr,
)


class TestGhResult:
    """Tests for GhResult dataclass."""

    def test_is_frozen(self) -> None:
        """Test GhResult is immutable."""
        result = GhResult(success=True, data=None, error=None)
        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]


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
            mock_auth.stderr = (
                "You are not logged into any GitHub hosts. To log in, run: gh auth login"
            )

            mock_run.side_effect = [mock_version, mock_auth]

            available, message = check_gh_availability()
            assert available is False
            assert "auth" in message.lower()

    def test_gh_auth_failure_includes_stderr(self) -> None:
        """Test that auth failure message includes actual stderr from gh auth status."""
        with patch("subprocess.run") as mock_run:
            mock_version = MagicMock()
            mock_version.returncode = 0

            mock_auth = MagicMock()
            mock_auth.returncode = 1
            mock_auth.stderr = "Failed to log in to github.com using token (GH_TOKEN)\nThe token in GH_TOKEN is invalid."

            mock_run.side_effect = [mock_version, mock_auth]

            available, message = check_gh_availability()
            assert available is False
            assert "GH_TOKEN is invalid" in message


class TestRunGh:
    """Tests for _run_gh helper."""

    @patch("issue_workflow.services.github.subprocess.run")
    def test_success_with_json_parsing(self, mock_run: MagicMock) -> None:
        """Test successful execution with JSON parsing."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"number": 1, "title": "test"})
        mock_run.return_value = mock_result

        result = _run_gh(["gh", "issue", "view", "1"])
        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, dict)
        assert result.data["number"] == 1

    @patch("issue_workflow.services.github.subprocess.run")
    def test_nonzero_returncode_returns_error(self, mock_run: MagicMock) -> None:
        """Test non-zero returncode returns error GhResult."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "not found"
        mock_run.return_value = mock_result

        result = _run_gh(["gh", "issue", "view", "999"])
        assert result.success is False
        assert result.error == "not found"

    @patch("issue_workflow.services.github.subprocess.run")
    def test_parse_json_false_returns_output(self, mock_run: MagicMock) -> None:
        """Test parse_json=False returns stdout in data dict."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Merged successfully"
        mock_run.return_value = mock_result

        result = _run_gh(["gh", "pr", "merge", "1"], parse_json=False)
        assert result.success is True
        assert result.data == {"output": "Merged successfully"}

    @patch("issue_workflow.services.github.subprocess.run")
    def test_timeout_parameter_passed(self, mock_run: MagicMock) -> None:
        """Test timeout parameter is forwarded to subprocess.run."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "{}"
        mock_run.return_value = mock_result

        _run_gh(["gh", "pr", "checks", "1"], timeout=600)
        assert mock_run.call_args.kwargs.get("timeout") == 600

    @patch("issue_workflow.services.github.subprocess.run")
    def test_timeout_expired_returns_error(self, mock_run: MagicMock) -> None:
        """Test TimeoutExpired returns error GhResult."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=600)

        result = _run_gh(["gh", "pr", "checks", "1"], timeout=600)
        assert result.success is False
        assert "Timed out" in (result.error or "")

    @patch("issue_workflow.services.github.subprocess.run")
    def test_invalid_json_returns_error(self, mock_run: MagicMock) -> None:
        """Test invalid JSON response returns error GhResult."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not json"
        mock_run.return_value = mock_result

        result = _run_gh(["gh", "issue", "view", "1"])
        assert result.success is False
        assert "Invalid JSON" in (result.error or "")

    @patch("issue_workflow.services.github.subprocess.run")
    def test_subprocess_error_returns_error(self, mock_run: MagicMock) -> None:
        """Test SubprocessError returns error GhResult."""
        mock_run.side_effect = subprocess.SubprocessError("process error")

        result = _run_gh(["gh", "issue", "view", "1"])
        assert result.success is False
        assert "process error" in (result.error or "")


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
