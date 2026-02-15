"""Unit tests for respond-comments subcommand."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
)

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.respond_comments"


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


class TestRespondCommentsBasic:
    """Basic behavior tests for respond-comments."""

    def test_calls_detect_pr_number(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """detect_pr_number is called with the provided pr_number."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=300, verbose=False, timeout=3600)

        mock_pr_detector.assert_called_once_with(300)

    def test_calls_detect_pr_number_with_none(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """detect_pr_number is called with None when pr_number omitted."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=None, verbose=False, timeout=3600)

        mock_pr_detector.assert_called_once_with(None)

    def test_run_skill_called_with_command_name(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """run_claude_skill is called with command_name='respond-comments'."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=300, verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][0] == "respond-comments"

    def test_run_skill_called_with_review_pr_comments_prompt(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """run_claude_skill is called with '/review-pr-comments {pr_number}'."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=None, verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][1] == "/review-pr-comments 300"

    def test_run_skill_log_args_contain_pr_number(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """run_claude_skill log_args contains pr_number."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=300, verbose=False, timeout=3600)

        assert mock_run_skill.call_args[0][2] == {"pr_number": 300}

    def test_returns_zero_exit_code_on_success(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Returns exit_code=0 when run_claude_skill returns 0."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        exit_code = _run_respond_comments(pr_number=None, verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_when_claude_fails(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Returns nonzero exit_code when run_claude_skill returns nonzero."""
        mock_run_skill.return_value = 1

        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        exit_code = _run_respond_comments(pr_number=None, verbose=False, timeout=3600)

        assert exit_code == 1


class TestRespondCommentsDependencies:
    """Tests for dependency checking."""

    def test_pr_number_none_requires_claude_and_gh(
        self,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """pr_number=None requires claude + gh."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.respond_comments import (
                _run_respond_comments,
            )

            _run_respond_comments(pr_number=None, verbose=False, timeout=3600)

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg

    def test_pr_number_explicit_requires_claude_only(
        self,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Explicit pr_number requires only claude (no gh for auto-detection)."""
        with patch(f"{_MOD}.check_dependencies") as mock_deps:
            from issue_workflow.cli.commands.respond_comments import (
                _run_respond_comments,
            )

            _run_respond_comments(pr_number=300, verbose=False, timeout=3600)

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY not in deps_arg


class TestRespondCommentsVerbose:
    """Verbose mode tests."""

    def test_verbose_forwarded_to_run_skill(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """verbose=True is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=300, verbose=True, timeout=3600)

        assert mock_run_skill.call_args.kwargs.get("verbose") is True


class TestRespondCommentsTimeout:
    """Timeout option tests."""

    def test_custom_timeout_forwarded_to_run_skill(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Custom --timeout value is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=300, verbose=False, timeout=600)

        assert mock_run_skill.call_args.kwargs.get("timeout") == 600

    def test_default_timeout_is_3600(
        self,
        mock_deps: MagicMock,
        mock_run_skill: MagicMock,
        mock_pr_detector: MagicMock,
    ) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.respond_comments import _run_respond_comments

        _run_respond_comments(pr_number=300, verbose=False, timeout=DEFAULT_TIMEOUT_SECONDS)

        assert mock_run_skill.call_args.kwargs.get("timeout") == 3600
