"""Integration tests for PR merge operations."""

from unittest.mock import MagicMock, patch

from issue_workflow.services.github import merge_pr, wait_for_checks


class TestMergePr:
    """Tests for PR merge operations."""

    def test_merge_pr_squash_success(self) -> None:
        """Test successful squash merge."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Merged PR #100"
            mock_run.return_value = mock_result

            result = merge_pr(100, strategy="squash")
            assert result.success is True

            # Verify correct arguments
            call_args = mock_run.call_args[0][0]
            assert "merge" in call_args
            assert "--squash" in call_args
            assert "--delete-branch" in call_args

    def test_merge_pr_merge_strategy(self) -> None:
        """Test merge commit strategy."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Merged"
            mock_run.return_value = mock_result

            result = merge_pr(100, strategy="merge")
            assert result.success is True

            call_args = mock_run.call_args[0][0]
            assert "--merge" in call_args

    def test_merge_pr_rebase_strategy(self) -> None:
        """Test rebase merge strategy."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Rebased"
            mock_run.return_value = mock_result

            result = merge_pr(100, strategy="rebase")
            assert result.success is True

            call_args = mock_run.call_args[0][0]
            assert "--rebase" in call_args

    def test_merge_pr_without_delete_branch(self) -> None:
        """Test merge without deleting branch."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Merged"
            mock_run.return_value = mock_result

            result = merge_pr(100, delete_branch=False)
            assert result.success is True

            call_args = mock_run.call_args[0][0]
            assert "--delete-branch" not in call_args

    def test_merge_pr_conflict(self) -> None:
        """Test merge with conflict."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Pull request has conflicts"
            mock_run.return_value = mock_result

            result = merge_pr(100)
            assert result.success is False
            assert "conflict" in result.error.lower() if result.error else False


class TestWaitForChecks:
    """Tests for waiting for CI checks."""

    def test_wait_for_checks_success(self) -> None:
        """Test successful wait for checks."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "All checks passed"
            mock_run.return_value = mock_result

            result = wait_for_checks(100)
            assert result.success is True

    def test_wait_for_checks_failure(self) -> None:
        """Test wait for checks with failures."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Some checks failed"
            mock_run.return_value = mock_result

            result = wait_for_checks(100)
            assert result.success is False

    def test_wait_for_checks_timeout(self) -> None:
        """Test wait for checks timeout."""
        import subprocess

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=600)

            result = wait_for_checks(100, timeout=600)
            assert result.success is False
            assert result.error is not None
            assert "timed out" in result.error.lower()
