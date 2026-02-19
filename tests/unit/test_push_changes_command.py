"""Unit tests for push-changes subcommand."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    HACHIMOKU_DEPENDENCY,
)

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.push_changes"


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


@pytest.fixture()
def mock_pr_detector() -> Iterator[MagicMock]:
    """Mock detect_pr_number to return 300."""
    with patch(f"{_MOD}.detect_pr_number", return_value=300) as m:
        yield m


class TestPushChangesBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude_and_gh(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Dependency check includes CLAUDE_DEPENDENCY and GH_DEPENDENCY."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY in deps_arg

    def test_does_not_require_hachimoku(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Dependency check does not include HACHIMOKU_DEPENDENCY."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        deps_arg = mock_deps.call_args[0][0]
        assert HACHIMOKU_DEPENDENCY not in deps_arg

    def test_calls_detect_pr_number(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """detect_pr_number is called for auto-detection (FR-015a)."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        mock_pr_detector.assert_called_once()

    def test_run_skill_called_with_command_name(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """run_claude_skill is called with command_name='push-changes'."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][0] == "push-changes"

    def test_run_skill_called_with_push_prompt(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """run_claude_skill prompt contains /commit-push-pr."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        prompt = mock_run_skill.call_args[0][1]
        assert "/commit-push-pr" in prompt

    def test_prompt_contains_pr_skip_instruction(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Prompt contains instruction to skip PR creation."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        prompt = mock_run_skill.call_args[0][1]
        assert "PR" in prompt
        assert "スキップ" in prompt or "skip" in prompt.lower()

    def test_run_skill_log_args_contain_pr_number(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """run_claude_skill log_args contains pr_number."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][2] == {"pr_number": 300}

    def test_returns_zero_exit_code_on_success(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Returns exit_code=0 when run_claude_skill returns 0."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        exit_code = _run_push_changes(verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Returns exit_code=1 when run_claude_skill returns 1."""
        mock_run_skill.return_value = 1

        from issue_workflow.cli.commands.push_changes import _run_push_changes

        exit_code = _run_push_changes(verbose=False, timeout=3600)

        assert exit_code == 1


class TestPushChangesVerbose:
    """Verbose mode tests."""

    def test_verbose_forwarded_to_run_skill(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """verbose=True is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=True, timeout=3600)

        assert mock_run_skill.call_args.kwargs.get("verbose") is True


class TestPushChangesTimeout:
    """Timeout option tests."""

    def test_custom_timeout_forwarded_to_run_skill(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Custom --timeout value is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=600)

        assert mock_run_skill.call_args.kwargs.get("timeout") == 600

    def test_default_timeout_is_3600(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.push_changes import _run_push_changes

        _run_push_changes(verbose=False, timeout=DEFAULT_TIMEOUT_SECONDS)

        assert mock_run_skill.call_args.kwargs.get("timeout") == 3600


class TestPushChangesErrorHandling:
    """Error handling tests."""

    def test_pr_detection_failure_propagates_exit(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
    ) -> None:
        """typer.Exit from detect_pr_number propagates through _run_push_changes."""
        import typer

        with patch(f"{_MOD}.detect_pr_number", side_effect=typer.Exit(code=1)):
            from issue_workflow.cli.commands.push_changes import _run_push_changes

            with pytest.raises(typer.Exit) as exc_info:
                _run_push_changes(verbose=False, timeout=3600)

            assert exc_info.value.exit_code == 1
            mock_run_skill.assert_not_called()
