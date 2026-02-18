"""Unit tests for create-pr subcommand."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import CLAUDE_DEPENDENCY, GH_DEPENDENCY

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.create_pr"


@pytest.fixture()
def mock_deps() -> Iterator[MagicMock]:
    """Mock check_dependencies to do nothing."""
    with patch(f"{_MOD}.check_dependencies") as m:
        yield m


@pytest.fixture()
def mock_run_skill() -> Iterator[MagicMock]:
    """Mock run_claude_skill to return 0."""
    with patch(f"{_MOD}.run_claude_skill", return_value=0) as m:
        yield m


class TestCreatePrBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude_only(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Dependency check includes only CLAUDE_DEPENDENCY."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY not in deps_arg

    def test_run_skill_called_with_command_name(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """run_claude_skill is called with command_name='create-pr'."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][0] == "create-pr"

    def test_run_skill_called_with_prompt(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """run_claude_skill is called with '/commit-push-pr' prompt."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][1] == "/commit-push-pr"

    def test_run_skill_called_with_empty_log_args(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """run_claude_skill is called with empty log_args dict."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][2] == {}

    def test_returns_zero_exit_code_on_success(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Returns exit_code=0 when run_claude_skill returns 0."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        exit_code = _run_create_pr(verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Returns exit_code=1 when run_claude_skill returns 1."""
        mock_run_skill.return_value = 1

        from issue_workflow.cli.commands.create_pr import _run_create_pr

        exit_code = _run_create_pr(verbose=False, timeout=3600)

        assert exit_code == 1


class TestCreatePrVerbose:
    """Verbose mode tests."""

    def test_verbose_forwarded_to_run_skill(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """verbose=True is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=True, timeout=3600)

        assert mock_run_skill.call_args.kwargs.get("verbose") is True


class TestCreatePrTimeout:
    """Timeout option tests."""

    def test_custom_timeout_forwarded_to_run_skill(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Custom timeout value is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=600)

        assert mock_run_skill.call_args.kwargs.get("timeout") == 600

    def test_default_timeout_is_3600(self, mock_deps: MagicMock, mock_run_skill: MagicMock) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.create_pr import _run_create_pr

        _run_create_pr(verbose=False, timeout=DEFAULT_TIMEOUT_SECONDS)

        assert mock_run_skill.call_args.kwargs.get("timeout") == 3600
