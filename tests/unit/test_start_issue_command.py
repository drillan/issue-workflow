"""Unit tests for start-issue subcommand."""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS
from issue_workflow.services.dependency_checker import CLAUDE_DEPENDENCY, GH_DEPENDENCY

# Module path prefix for patching
_MOD = "issue_workflow.cli.commands.start_issue"


@pytest.fixture()
def mock_deps() -> Iterator[MagicMock]:
    """Mock check_dependencies to do nothing."""
    with patch(f"{_MOD}.check_dependencies") as m:
        yield m


@pytest.fixture()
def mock_run_skill() -> Iterator[MagicMock]:
    """Mock run_claude_skill with a successful return."""
    with patch(f"{_MOD}.run_claude_skill", return_value=0) as m:
        yield m


class TestStartIssueBasic:
    """Basic behavior tests."""

    def test_calls_check_dependencies_with_claude(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Dependency check includes CLAUDE_DEPENDENCY."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_deps.assert_called_once()
        deps_arg = mock_deps.call_args[0][0]
        assert CLAUDE_DEPENDENCY in deps_arg
        assert GH_DEPENDENCY not in deps_arg

    def test_calls_run_claude_skill_with_correct_args(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """run_claude_skill is called with correct command_name and prompt."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        mock_run_skill.assert_called_once()
        call_args = mock_run_skill.call_args
        assert call_args[0][0] == "start-issue"
        assert call_args[0][1] == "/start-issue 199 --force"

    def test_log_args_contain_issue_number_and_worktree(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """run_claude_skill log_args contains issue_number and worktree."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        log_args = mock_run_skill.call_args[0][2]
        assert log_args["issue_number"] == 199
        assert log_args["worktree"] is False

    def test_returns_zero_exit_code_on_success(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Returns exit_code=0 when run_claude_skill returns 0."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        exit_code = _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 0

    def test_returns_nonzero_exit_code_on_failure(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Returns exit_code=1 when run_claude_skill returns 1."""
        mock_run_skill.return_value = 1

        from issue_workflow.cli.commands.start_issue import _run_start_issue

        exit_code = _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        assert exit_code == 1


class TestStartIssueVerbose:
    """Verbose mode tests."""

    def test_verbose_passed_to_run_claude_skill(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """verbose=True is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=True, timeout=3600)

        call_kwargs = mock_run_skill.call_args
        assert call_kwargs.kwargs.get("verbose") is True


class TestStartIssueTimeout:
    """Timeout option tests."""

    def test_custom_timeout_passed_to_run_claude_skill(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Custom --timeout value is forwarded to run_claude_skill."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=600)

        call_kwargs = mock_run_skill.call_args
        assert call_kwargs.kwargs.get("timeout") == 600

    def test_default_timeout_is_3600(self, mock_deps: MagicMock, mock_run_skill: MagicMock) -> None:
        """Default timeout is DEFAULT_TIMEOUT_SECONDS (3600)."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(
            issue_number=199,
            worktree=False,
            verbose=False,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        call_kwargs = mock_run_skill.call_args
        assert call_kwargs.kwargs.get("timeout") == 3600


class TestStartIssueWorktree:
    """Worktree option tests."""

    def test_worktree_adds_gh_dependency(self, mock_run_skill: MagicMock) -> None:
        """--worktree adds GH_DEPENDENCY to dependency check."""
        with (
            patch(f"{_MOD}.check_dependencies") as mock_deps,
            patch(f"{_MOD}.find_worktree_for_branch", return_value=Path("/tmp/wt")),
        ):
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            deps_arg = mock_deps.call_args[0][0]
            assert CLAUDE_DEPENDENCY in deps_arg
            assert GH_DEPENDENCY in deps_arg

    def test_worktree_detects_existing_worktree(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Existing worktree is detected and used as cwd."""
        existing_path = Path("/tmp/existing-wt")

        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=existing_path),
            patch(f"{_MOD}.GitOperations"),
        ):
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            call_kwargs = mock_run_skill.call_args
            assert call_kwargs.kwargs.get("cwd") == existing_path

    def test_worktree_creates_new_when_not_found(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """New worktree is created when not found."""
        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(f"{_MOD}.copy_hachimoku_to_worktree"),
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            mock_git.worktree_add.assert_called_once()

    def test_worktree_copies_hachimoku(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """copy_hachimoku_to_worktree is called after worktree creation."""
        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(f"{_MOD}.copy_hachimoku_to_worktree") as mock_copy,
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            mock_copy.assert_called_once()

    def test_worktree_sets_cwd_for_run_claude_skill(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Worktree path is passed as cwd to run_claude_skill."""
        wt_path = Path("/tmp/worktree-199")

        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=wt_path),
            patch(f"{_MOD}.GitOperations"),
        ):
            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            call_kwargs = mock_run_skill.call_args
            assert call_kwargs.kwargs.get("cwd") == wt_path

    def test_no_worktree_sets_cwd_none(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Without --worktree, cwd is not passed (defaults in run_claude_skill)."""
        from issue_workflow.cli.commands.start_issue import _run_start_issue

        _run_start_issue(issue_number=199, worktree=False, verbose=False, timeout=3600)

        call_kwargs = mock_run_skill.call_args
        # cwd should not be in kwargs (not passed when no worktree)
        assert call_kwargs.kwargs.get("cwd") is None


class TestStartIssueErrorHandling:
    """Error handling tests."""

    def test_worktree_git_error_shows_message_and_exits(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """GitError in _prepare_worktree prints error and returns 1."""
        from issue_workflow.lib.git import GitError

        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(f"{_MOD}.ui") as mock_ui,
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git.worktree_add.side_effect = GitError("branch already exists")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            exit_code = _run_start_issue(
                issue_number=199, worktree=True, verbose=False, timeout=3600
            )

            assert exit_code == 1
            error_calls = [str(c) for c in mock_ui.print_error.call_args_list]
            assert any("worktree" in c.lower() for c in error_calls)


class TestStartIssueCopyHachimokuError:
    """Tests for OSError from copy_hachimoku_to_worktree (Issue #112)."""

    def test_copy_hachimoku_os_error_returns_1(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """OSError from copy_hachimoku_to_worktree returns exit code 1."""
        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(
                f"{_MOD}.copy_hachimoku_to_worktree",
                side_effect=OSError("disk full"),
            ),
            patch(f"{_MOD}.ui") as mock_ui,
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            exit_code = _run_start_issue(
                issue_number=199, worktree=True, verbose=False, timeout=3600
            )

            assert exit_code == 1
            mock_ui.print_error.assert_called_once()
            mock_run_skill.assert_not_called()

    def test_copy_hachimoku_os_error_message_contains_detail(
        self, mock_deps: MagicMock, mock_run_skill: MagicMock
    ) -> None:
        """Error message includes the OSError detail."""
        with (
            patch(f"{_MOD}.find_worktree_for_branch", return_value=None),
            patch(f"{_MOD}.GitOperations") as mock_git_cls,
            patch(
                f"{_MOD}.copy_hachimoku_to_worktree",
                side_effect=OSError("permission denied"),
            ),
            patch(f"{_MOD}.ui") as mock_ui,
        ):
            mock_git = MagicMock()
            mock_git.repo_path = Path("/tmp/repo")
            mock_git_cls.return_value = mock_git

            from issue_workflow.cli.commands.start_issue import _run_start_issue

            _run_start_issue(issue_number=199, worktree=True, verbose=False, timeout=3600)

            error_msg = str(mock_ui.print_error.call_args)
            assert "permission denied" in error_msg.lower()
