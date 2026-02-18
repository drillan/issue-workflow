"""Unit tests for WorkflowContext dataclass."""

from pathlib import Path

import pytest

from issue_workflow.models.claude_result import ClaudeResult
from tests.conftest import make_claude_result


def _make_result_with_cost(cost: float) -> ClaudeResult:
    """Create a ClaudeResult with a specific total_cost_usd."""
    return ClaudeResult(
        type="result",
        subtype="success",
        total_cost_usd=cost,
        exit_code=0,
        raw_json="{}",
    )


class TestWorkflowContextHasError:
    """Tests for has_error property."""

    def test_no_results_has_no_error(self) -> None:
        """Empty step_results means no error."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.has_error is False

    def test_all_success_has_no_error(self) -> None:
        """All successful results means no error."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)
        ctx.step_results.append(make_claude_result(exit_code=0))

        assert ctx.has_error is False

    def test_exit_code_nonzero_has_error(self) -> None:
        """Non-zero exit_code means has_error is True."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)
        ctx.step_results.append(make_claude_result(exit_code=1, is_error=True))

        assert ctx.has_error is True

    def test_is_error_true_has_error(self) -> None:
        """is_error=True with exit_code=0 still means has_error is True."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)
        ctx.step_results.append(make_claude_result(exit_code=0, is_error=True))

        assert ctx.has_error is True

    def test_mixed_results_has_error(self) -> None:
        """One error among successes means has_error is True."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)
        ctx.step_results.append(make_claude_result(exit_code=0))
        ctx.step_results.append(make_claude_result(exit_code=1, is_error=True))

        assert ctx.has_error is True


class TestWorkflowContextLastResult:
    """Tests for last_result property."""

    def test_empty_results_returns_none(self) -> None:
        """Empty step_results returns None."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.last_result is None

    def test_returns_most_recent_result(self) -> None:
        """Returns the last appended result."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)
        r1 = make_claude_result(exit_code=0)
        r2 = make_claude_result(exit_code=1, is_error=True)
        ctx.step_results.append(r1)
        ctx.step_results.append(r2)

        assert ctx.last_result is r2


class TestWorkflowContextTotalCost:
    """Tests for total_cost_usd property."""

    def test_empty_results_returns_zero(self) -> None:
        """Empty step_results returns 0.0."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.total_cost_usd == 0.0

    def test_aggregates_cost_across_results(self) -> None:
        """Sums total_cost_usd from all results."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)
        ctx.step_results.append(_make_result_with_cost(0.05))
        ctx.step_results.append(_make_result_with_cost(0.10))

        assert ctx.total_cost_usd == pytest.approx(0.15)


class TestWorkflowContextCwd:
    """Tests for cwd_for_skill and cwd_for_merge properties."""

    def test_cwd_for_skill_none_without_worktree(self) -> None:
        """cwd_for_skill is None when no worktree_path."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.cwd_for_skill is None

    def test_cwd_for_skill_returns_worktree_path(self) -> None:
        """cwd_for_skill returns worktree_path when set."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199, worktree_path=Path("/tmp/wt"))

        assert ctx.cwd_for_skill == Path("/tmp/wt")

    def test_cwd_for_merge_always_none(self) -> None:
        """cwd_for_merge is always None (main repo) even with worktree."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199, worktree_path=Path("/tmp/wt"))

        assert ctx.cwd_for_merge is None

    def test_cwd_for_merge_none_without_worktree(self) -> None:
        """cwd_for_merge is None without worktree."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.cwd_for_merge is None


class TestWorkflowContextLogNumber:
    """Tests for log_number_for_step method."""

    def test_start_issue_returns_issue_number(self) -> None:
        """start-issue uses issue_number for log filename."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.log_number_for_step("start-issue") == 199

    def test_review_pr_returns_pr_number(self) -> None:
        """review-pr uses pr_number for log filename."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199, pr_number=300)

        assert ctx.log_number_for_step("review-pr") == 300

    def test_respond_comments_returns_pr_number(self) -> None:
        """respond-comments uses pr_number for log filename."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199, pr_number=300)

        assert ctx.log_number_for_step("respond-comments") == 300

    def test_merge_pr_returns_pr_number(self) -> None:
        """merge-pr uses pr_number for log filename."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199, pr_number=300)

        assert ctx.log_number_for_step("merge-pr") == 300

    def test_create_pr_returns_none(self) -> None:
        """create-pr returns None (no number in log filename)."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.log_number_for_step("create-pr") is None

    def test_push_changes_returns_none(self) -> None:
        """push-changes returns None (no number in log filename)."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.log_number_for_step("push-changes") is None

    def test_pr_number_none_returns_none_for_pr_commands(self) -> None:
        """PR-related commands return None when pr_number not set."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.log_number_for_step("review-pr") is None


class TestWorkflowContextDefaults:
    """Tests for default values."""

    def test_pr_number_defaults_to_none(self) -> None:
        """pr_number defaults to None."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.pr_number is None

    def test_worktree_path_defaults_to_none(self) -> None:
        """worktree_path defaults to None."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.worktree_path is None

    def test_step_results_defaults_to_empty_list(self) -> None:
        """step_results defaults to empty list."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx = WorkflowContext(issue_number=199)

        assert ctx.step_results == []

    def test_step_results_independent_per_instance(self) -> None:
        """Each instance has its own step_results list."""
        from issue_workflow.models.workflow_context import WorkflowContext

        ctx1 = WorkflowContext(issue_number=199)
        ctx2 = WorkflowContext(issue_number=200)
        ctx1.step_results.append(make_claude_result())

        assert len(ctx2.step_results) == 0
