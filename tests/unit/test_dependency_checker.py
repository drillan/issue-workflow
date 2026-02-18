"""Unit tests for DependencyInfo and check_dependencies."""

from unittest.mock import MagicMock, patch

import pytest
import typer

from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    HACHIMOKU_DEPENDENCY,
    DependencyInfo,
    check_dependencies,
)


class TestDependencyInfo:
    """Tests for DependencyInfo dataclass."""

    def test_frozen_immutability(self) -> None:
        """Test DependencyInfo fields cannot be modified."""
        dep = DependencyInfo(command="test", install_hint="install test", check_auth=False)
        with pytest.raises(AttributeError):
            dep.command = "modified"  # type: ignore[misc]

    def test_predefined_claude_dependency(self) -> None:
        """Test CLAUDE_DEPENDENCY constant values."""
        assert CLAUDE_DEPENDENCY.command == "claude"
        assert "anthropic.com" in CLAUDE_DEPENDENCY.install_hint
        assert CLAUDE_DEPENDENCY.check_auth is False

    def test_predefined_gh_dependency(self) -> None:
        """Test GH_DEPENDENCY constant values."""
        assert GH_DEPENDENCY.command == "gh"
        assert "cli.github.com" in GH_DEPENDENCY.install_hint
        assert GH_DEPENDENCY.check_auth is True

    def test_predefined_hachimoku_dependency(self) -> None:
        """Test HACHIMOKU_DEPENDENCY constant values."""
        assert HACHIMOKU_DEPENDENCY.command == "8moku"
        assert "uv tool install hachimoku" in HACHIMOKU_DEPENDENCY.install_hint
        assert HACHIMOKU_DEPENDENCY.check_auth is False


class TestCheckDependencies:
    """Tests for check_dependencies function."""

    @patch("issue_workflow.services.dependency_checker.shutil.which")
    def test_all_dependencies_available(self, mock_which: MagicMock) -> None:
        """Test no error when all dependencies found."""
        mock_which.return_value = "/usr/bin/test"
        deps = [DependencyInfo(command="test-cmd", install_hint="install it", check_auth=False)]
        # Should not raise
        check_dependencies(deps)

    @patch("issue_workflow.services.dependency_checker.shutil.which")
    def test_single_missing_dependency_raises_system_exit(self, mock_which: MagicMock) -> None:
        """Test SystemExit raised when dependency is missing."""
        mock_which.return_value = None
        deps = [DependencyInfo(command="missing-cmd", install_hint="install it", check_auth=False)]
        with pytest.raises(typer.Exit):
            check_dependencies(deps)

    @patch("issue_workflow.services.dependency_checker.shutil.which")
    def test_missing_dependency_shows_install_hint(self, mock_which: MagicMock) -> None:
        """Test error message includes install hint."""
        mock_which.return_value = None
        deps = [
            DependencyInfo(
                command="missing-cmd",
                install_hint="https://example.com/install",
                check_auth=False,
            )
        ]
        with pytest.raises(typer.Exit):
            check_dependencies(deps)

    @patch("issue_workflow.services.dependency_checker.check_gh_availability")
    @patch("issue_workflow.services.dependency_checker.shutil.which")
    def test_check_auth_calls_check_gh_availability(
        self, mock_which: MagicMock, mock_gh_check: MagicMock
    ) -> None:
        """Test check_auth=True triggers check_gh_availability."""
        mock_which.return_value = "/usr/bin/gh"
        mock_gh_check.return_value = (True, "GitHub CLI is available and authenticated")
        deps = [GH_DEPENDENCY]
        check_dependencies(deps)
        mock_gh_check.assert_called_once()

    @patch("issue_workflow.services.dependency_checker.check_gh_availability")
    @patch("issue_workflow.services.dependency_checker.shutil.which")
    def test_gh_auth_failure_raises_system_exit(
        self, mock_which: MagicMock, mock_gh_check: MagicMock
    ) -> None:
        """Test SystemExit when gh auth check fails."""
        mock_which.return_value = "/usr/bin/gh"
        mock_gh_check.return_value = (False, "GitHub CLI authentication failed")
        deps = [GH_DEPENDENCY]
        with pytest.raises(typer.Exit):
            check_dependencies(deps)

    @patch("issue_workflow.services.dependency_checker.shutil.which")
    def test_multiple_missing_shows_all_hints(self, mock_which: MagicMock) -> None:
        """Test error message includes all missing dependencies."""
        mock_which.return_value = None
        deps = [
            DependencyInfo(command="cmd1", install_hint="hint1", check_auth=False),
            DependencyInfo(command="cmd2", install_hint="hint2", check_auth=False),
        ]
        with pytest.raises(typer.Exit):
            check_dependencies(deps)
