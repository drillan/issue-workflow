"""Unit tests for ReviewResult models."""

import pytest

from issue_workflow.models.review import (
    AgentResultStatus,
    ReviewAgentResult,
    ReviewIssue,
    ReviewIssueLocation,
    ReviewMode,
    ReviewResult,
    ReviewSeverity,
    ReviewSummary,
)


class TestReviewMode:
    """Tests for ReviewMode enum."""

    def test_diff_value(self) -> None:
        assert ReviewMode.DIFF.value == "diff"

    def test_pr_value(self) -> None:
        assert ReviewMode.PR.value == "pr"

    def test_from_string(self) -> None:
        assert ReviewMode("diff") == ReviewMode.DIFF
        assert ReviewMode("pr") == ReviewMode.PR

    def test_invalid_value_raises_error(self) -> None:
        with pytest.raises(ValueError):
            ReviewMode("invalid")


class TestAgentResultStatus:
    """Tests for AgentResultStatus enum."""

    def test_success_value(self) -> None:
        assert AgentResultStatus.SUCCESS.value == "success"

    def test_error_value(self) -> None:
        assert AgentResultStatus.ERROR.value == "error"

    def test_from_string(self) -> None:
        assert AgentResultStatus("success") == AgentResultStatus.SUCCESS

    def test_invalid_value_raises_error(self) -> None:
        with pytest.raises(ValueError):
            AgentResultStatus("unknown")


class TestReviewSeverity:
    """Tests for ReviewSeverity enum."""

    def test_critical_value(self) -> None:
        assert ReviewSeverity.CRITICAL.value == "Critical"

    def test_important_value(self) -> None:
        assert ReviewSeverity.IMPORTANT.value == "Important"

    def test_suggestion_value(self) -> None:
        assert ReviewSeverity.SUGGESTION.value == "Suggestion"

    def test_nitpick_value(self) -> None:
        assert ReviewSeverity.NITPICK.value == "Nitpick"

    def test_from_string(self) -> None:
        assert ReviewSeverity("Critical") == ReviewSeverity.CRITICAL
        assert ReviewSeverity("Nitpick") == ReviewSeverity.NITPICK

    def test_invalid_value_raises_error(self) -> None:
        with pytest.raises(ValueError):
            ReviewSeverity("invalid")


class TestReviewIssueLocation:
    """Tests for ReviewIssueLocation dataclass."""

    def test_creation(self) -> None:
        location = ReviewIssueLocation(file_path="src/main.py", line_number=42)
        assert location.file_path == "src/main.py"
        assert location.line_number == 42

    def test_is_frozen(self) -> None:
        location = ReviewIssueLocation(file_path="src/main.py", line_number=42)
        with pytest.raises(AttributeError):
            location.file_path = "other.py"  # type: ignore[misc]


class TestReviewIssue:
    """Tests for ReviewIssue dataclass."""

    def test_creation_with_all_fields(self) -> None:
        location = ReviewIssueLocation(file_path="src/main.py", line_number=10)
        issue = ReviewIssue(
            agent_name="security-agent",
            severity=ReviewSeverity.CRITICAL,
            description="SQL injection vulnerability",
            location=location,
            suggestion="Use parameterized queries",
            category="security",
        )
        assert issue.agent_name == "security-agent"
        assert issue.severity == ReviewSeverity.CRITICAL
        assert issue.description == "SQL injection vulnerability"
        assert issue.location is not None
        assert issue.location.file_path == "src/main.py"
        assert issue.suggestion == "Use parameterized queries"
        assert issue.category == "security"

    def test_creation_with_required_fields_only(self) -> None:
        issue = ReviewIssue(
            agent_name="style-agent",
            severity=ReviewSeverity.SUGGESTION,
            description="Consider renaming variable",
        )
        assert issue.agent_name == "style-agent"
        assert issue.location is None
        assert issue.suggestion is None
        assert issue.category is None

    def test_is_frozen(self) -> None:
        issue = ReviewIssue(
            agent_name="agent",
            severity=ReviewSeverity.IMPORTANT,
            description="desc",
        )
        with pytest.raises(AttributeError):
            issue.agent_name = "other"  # type: ignore[misc]


class TestReviewAgentResult:
    """Tests for ReviewAgentResult dataclass."""

    def test_success_result(self) -> None:
        issues = (
            ReviewIssue(
                agent_name="code-reviewer",
                severity=ReviewSeverity.IMPORTANT,
                description="issue 1",
            ),
        )
        result = ReviewAgentResult(
            status=AgentResultStatus.SUCCESS,
            agent_name="code-reviewer",
            issues=issues,
            elapsed_time=109.5,
        )
        assert result.status == AgentResultStatus.SUCCESS
        assert result.agent_name == "code-reviewer"
        assert len(result.issues) == 1
        assert result.elapsed_time == 109.5
        assert result.error_message is None

    def test_error_result(self) -> None:
        result = ReviewAgentResult(
            status=AgentResultStatus.ERROR,
            agent_name="pr-test-analyzer",
            issues=(),
            elapsed_time=156.1,
            error_message="Structured output recovery failed",
        )
        assert result.status == AgentResultStatus.ERROR
        assert result.error_message == "Structured output recovery failed"
        assert result.issues == ()

    def test_issues_is_tuple(self) -> None:
        """Test issues field is a tuple (immutable collection)."""
        issue = ReviewIssue(
            agent_name="code-reviewer",
            severity=ReviewSeverity.IMPORTANT,
            description="test issue",
        )
        result = ReviewAgentResult(
            status=AgentResultStatus.SUCCESS,
            agent_name="code-reviewer",
            issues=(issue,),
            elapsed_time=1.0,
        )
        assert isinstance(result.issues, tuple)

    def test_is_frozen(self) -> None:
        result = ReviewAgentResult(
            status=AgentResultStatus.SUCCESS,
            agent_name="agent",
            issues=(),
            elapsed_time=1.0,
        )
        with pytest.raises(AttributeError):
            result.status = AgentResultStatus.ERROR  # type: ignore[misc]


class TestReviewSummary:
    """Tests for ReviewSummary dataclass."""

    def test_creation(self) -> None:
        summary = ReviewSummary(
            total_issues=4,
            max_severity=ReviewSeverity.IMPORTANT,
            total_elapsed_time=109.5,
        )
        assert summary.total_issues == 4
        assert summary.max_severity == ReviewSeverity.IMPORTANT
        assert summary.total_elapsed_time == 109.5

    def test_null_max_severity(self) -> None:
        summary = ReviewSummary(
            total_issues=0,
            max_severity=None,
            total_elapsed_time=48.6,
        )
        assert summary.max_severity is None

    def test_is_frozen(self) -> None:
        summary = ReviewSummary(
            total_issues=1,
            max_severity=ReviewSeverity.SUGGESTION,
            total_elapsed_time=10.0,
        )
        with pytest.raises(AttributeError):
            summary.total_issues = 0  # type: ignore[misc]


class TestReviewResult:
    """Tests for ReviewResult dataclass."""

    def test_creation(self) -> None:
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="a" * 40,
            branch_name="feat/42-some-feature",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(),
            summary=ReviewSummary(
                total_issues=0,
                max_severity=None,
                total_elapsed_time=0.0,
            ),
        )
        assert result.review_mode == ReviewMode.DIFF
        assert result.commit_hash == "a" * 40
        assert result.branch_name == "feat/42-some-feature"
        assert result.results == ()

    def test_pr_mode_with_pr_number(self) -> None:
        result = ReviewResult(
            review_mode=ReviewMode.PR,
            commit_hash="b" * 40,
            branch_name="feat/1-test",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(),
            summary=ReviewSummary(
                total_issues=0,
                max_severity=None,
                total_elapsed_time=0.0,
            ),
            pr_number=210,
        )
        assert result.pr_number == 210

    def test_all_issues_empty(self) -> None:
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="a" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(),
            summary=ReviewSummary(
                total_issues=0,
                max_severity=None,
                total_elapsed_time=0.0,
            ),
        )
        assert result.all_issues == []

    def test_all_issues_flattens_across_agents(self) -> None:
        issue1 = ReviewIssue(
            agent_name="code-reviewer",
            severity=ReviewSeverity.IMPORTANT,
            description="issue from agent 1",
        )
        issue2 = ReviewIssue(
            agent_name="type-analyzer",
            severity=ReviewSeverity.SUGGESTION,
            description="issue from agent 2",
        )
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="c" * 40,
            branch_name="feat/1-test",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(
                ReviewAgentResult(
                    status=AgentResultStatus.SUCCESS,
                    agent_name="code-reviewer",
                    issues=(issue1,),
                    elapsed_time=100.0,
                ),
                ReviewAgentResult(
                    status=AgentResultStatus.SUCCESS,
                    agent_name="type-analyzer",
                    issues=(issue2,),
                    elapsed_time=50.0,
                ),
            ),
            summary=ReviewSummary(
                total_issues=2,
                max_severity=ReviewSeverity.IMPORTANT,
                total_elapsed_time=150.0,
            ),
        )
        assert len(result.all_issues) == 2
        assert result.all_issues[0].description == "issue from agent 1"
        assert result.all_issues[1].description == "issue from agent 2"

    def test_all_issues_skips_error_agents(self) -> None:
        issue = ReviewIssue(
            agent_name="code-reviewer",
            severity=ReviewSeverity.CRITICAL,
            description="critical issue",
        )
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="d" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(
                ReviewAgentResult(
                    status=AgentResultStatus.SUCCESS,
                    agent_name="code-reviewer",
                    issues=(issue,),
                    elapsed_time=100.0,
                ),
                ReviewAgentResult(
                    status=AgentResultStatus.ERROR,
                    agent_name="pr-test-analyzer",
                    issues=(),
                    elapsed_time=156.0,
                    error_message="Recovery failed",
                ),
            ),
            summary=ReviewSummary(
                total_issues=1,
                max_severity=ReviewSeverity.CRITICAL,
                total_elapsed_time=256.0,
            ),
        )
        assert len(result.all_issues) == 1

    def test_has_critical_true(self) -> None:
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="e" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(
                ReviewAgentResult(
                    status=AgentResultStatus.SUCCESS,
                    agent_name="agent",
                    issues=(
                        ReviewIssue(
                            agent_name="agent",
                            severity=ReviewSeverity.CRITICAL,
                            description="critical",
                        ),
                    ),
                    elapsed_time=1.0,
                ),
            ),
            summary=ReviewSummary(
                total_issues=1,
                max_severity=ReviewSeverity.CRITICAL,
                total_elapsed_time=1.0,
            ),
        )
        assert result.has_critical is True

    def test_has_critical_false(self) -> None:
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="f" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(
                ReviewAgentResult(
                    status=AgentResultStatus.SUCCESS,
                    agent_name="agent",
                    issues=(
                        ReviewIssue(
                            agent_name="agent",
                            severity=ReviewSeverity.SUGGESTION,
                            description="minor",
                        ),
                    ),
                    elapsed_time=1.0,
                ),
            ),
            summary=ReviewSummary(
                total_issues=1,
                max_severity=ReviewSeverity.SUGGESTION,
                total_elapsed_time=1.0,
            ),
        )
        assert result.has_critical is False

    def test_results_is_tuple(self) -> None:
        """Test results field is a tuple (immutable collection)."""
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="a" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(),
            summary=ReviewSummary(
                total_issues=0,
                max_severity=None,
                total_elapsed_time=0.0,
            ),
        )
        assert isinstance(result.results, tuple)

    def test_is_frozen(self) -> None:
        result = ReviewResult(
            review_mode=ReviewMode.DIFF,
            commit_hash="a" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            results=(),
            summary=ReviewSummary(
                total_issues=0,
                max_severity=None,
                total_elapsed_time=0.0,
            ),
        )
        with pytest.raises(AttributeError):
            result.review_mode = ReviewMode.PR  # type: ignore[misc]

    def test_invalid_review_mode_raises_error(self) -> None:
        with pytest.raises(ValueError):
            ReviewResult(
                review_mode=ReviewMode("invalid"),
                commit_hash="a" * 40,
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                results=(),
                summary=ReviewSummary(
                    total_issues=0,
                    max_severity=None,
                    total_elapsed_time=0.0,
                ),
            )

    def test_valid_review_modes(self) -> None:
        for mode in (ReviewMode.DIFF, ReviewMode.PR):
            result = ReviewResult(
                review_mode=mode,
                commit_hash="a" * 40,
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                results=(),
                summary=ReviewSummary(
                    total_issues=0,
                    max_severity=None,
                    total_elapsed_time=0.0,
                ),
            )
            assert result.review_mode == mode

    def test_invalid_commit_hash_length_raises_error(self) -> None:
        with pytest.raises(ValueError, match="commit_hash"):
            ReviewResult(
                review_mode=ReviewMode.DIFF,
                commit_hash="abc123",
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                results=(),
                summary=ReviewSummary(
                    total_issues=0,
                    max_severity=None,
                    total_elapsed_time=0.0,
                ),
            )

    def test_invalid_commit_hash_characters_raises_error(self) -> None:
        with pytest.raises(ValueError, match="commit_hash"):
            ReviewResult(
                review_mode=ReviewMode.DIFF,
                commit_hash="g" * 40,
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                results=(),
                summary=ReviewSummary(
                    total_issues=0,
                    max_severity=None,
                    total_elapsed_time=0.0,
                ),
            )
