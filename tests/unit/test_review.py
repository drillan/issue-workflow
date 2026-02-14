"""Unit tests for ReviewResult models (T068)."""

import pytest

from issue_workflow.models.review import (
    ReviewIssue,
    ReviewIssueLocation,
    ReviewResult,
    ReviewSeverity,
)


class TestReviewSeverity:
    """Tests for ReviewSeverity enum."""

    def test_critical_value(self) -> None:
        """Test CRITICAL enum value."""
        assert ReviewSeverity.CRITICAL.value == "Critical"

    def test_important_value(self) -> None:
        """Test IMPORTANT enum value."""
        assert ReviewSeverity.IMPORTANT.value == "Important"

    def test_suggestion_value(self) -> None:
        """Test SUGGESTION enum value."""
        assert ReviewSeverity.SUGGESTION.value == "Suggestion"

    def test_from_string(self) -> None:
        """Test ReviewSeverity can be created from string."""
        assert ReviewSeverity("Critical") == ReviewSeverity.CRITICAL

    def test_invalid_value_raises_error(self) -> None:
        """Test invalid severity value raises error."""
        with pytest.raises(ValueError):
            ReviewSeverity("invalid")


class TestReviewIssueLocation:
    """Tests for ReviewIssueLocation dataclass."""

    def test_creation(self) -> None:
        """Test creating a ReviewIssueLocation."""
        location = ReviewIssueLocation(file_path="src/main.py", line_number=42)
        assert location.file_path == "src/main.py"
        assert location.line_number == 42

    def test_is_frozen(self) -> None:
        """Test ReviewIssueLocation is immutable."""
        location = ReviewIssueLocation(file_path="src/main.py", line_number=42)
        with pytest.raises(AttributeError):
            location.file_path = "other.py"  # type: ignore[misc]


class TestReviewIssue:
    """Tests for ReviewIssue dataclass."""

    def test_creation_with_all_fields(self) -> None:
        """Test creating a ReviewIssue with all fields."""
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
        """Test creating a ReviewIssue with only required fields."""
        issue = ReviewIssue(
            agent_name="style-agent",
            severity=ReviewSeverity.SUGGESTION,
            description="Consider renaming variable",
        )
        assert issue.agent_name == "style-agent"
        assert issue.location is None
        assert issue.suggestion is None
        assert issue.category is None

    def test_location_is_optional(self) -> None:
        """Test location field defaults to None."""
        issue = ReviewIssue(
            agent_name="agent",
            severity=ReviewSeverity.IMPORTANT,
            description="desc",
        )
        assert issue.location is None

    def test_suggestion_is_optional(self) -> None:
        """Test suggestion field defaults to None."""
        issue = ReviewIssue(
            agent_name="agent",
            severity=ReviewSeverity.IMPORTANT,
            description="desc",
        )
        assert issue.suggestion is None

    def test_category_is_optional(self) -> None:
        """Test category field defaults to None."""
        issue = ReviewIssue(
            agent_name="agent",
            severity=ReviewSeverity.IMPORTANT,
            description="desc",
        )
        assert issue.category is None

    def test_is_frozen(self) -> None:
        """Test ReviewIssue is immutable."""
        issue = ReviewIssue(
            agent_name="agent",
            severity=ReviewSeverity.IMPORTANT,
            description="desc",
        )
        with pytest.raises(AttributeError):
            issue.agent_name = "other"  # type: ignore[misc]


class TestReviewResult:
    """Tests for ReviewResult dataclass."""

    def test_creation(self) -> None:
        """Test creating a ReviewResult."""
        result = ReviewResult(
            review_mode="diff",
            commit_hash="a" * 40,
            branch_name="feat/42-some-feature",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=[],
        )
        assert result.review_mode == "diff"
        assert result.commit_hash == "a" * 40
        assert result.branch_name == "feat/42-some-feature"
        assert result.reviewed_at == "2026-02-14T12:00:00Z"
        assert result.issues == []

    def test_issue_count_empty(self) -> None:
        """Test issue_count with no issues."""
        result = ReviewResult(
            review_mode="pr",
            commit_hash="b" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=[],
        )
        assert result.issue_count == 0

    def test_issue_count_with_issues(self) -> None:
        """Test issue_count with multiple issues."""
        issues = [
            ReviewIssue(
                agent_name="agent1",
                severity=ReviewSeverity.CRITICAL,
                description="issue 1",
            ),
            ReviewIssue(
                agent_name="agent2",
                severity=ReviewSeverity.SUGGESTION,
                description="issue 2",
            ),
        ]
        result = ReviewResult(
            review_mode="diff",
            commit_hash="c" * 40,
            branch_name="feat/1-test",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=issues,
        )
        assert result.issue_count == 2

    def test_has_critical_true(self) -> None:
        """Test has_critical returns True when critical issues exist."""
        issues = [
            ReviewIssue(
                agent_name="agent",
                severity=ReviewSeverity.CRITICAL,
                description="critical issue",
            ),
        ]
        result = ReviewResult(
            review_mode="diff",
            commit_hash="d" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=issues,
        )
        assert result.has_critical is True

    def test_has_critical_false(self) -> None:
        """Test has_critical returns False when no critical issues."""
        issues = [
            ReviewIssue(
                agent_name="agent",
                severity=ReviewSeverity.SUGGESTION,
                description="minor issue",
            ),
            ReviewIssue(
                agent_name="agent",
                severity=ReviewSeverity.IMPORTANT,
                description="important issue",
            ),
        ]
        result = ReviewResult(
            review_mode="pr",
            commit_hash="e" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=issues,
        )
        assert result.has_critical is False

    def test_has_critical_empty_issues(self) -> None:
        """Test has_critical returns False when no issues."""
        result = ReviewResult(
            review_mode="diff",
            commit_hash="f" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=[],
        )
        assert result.has_critical is False

    def test_is_frozen(self) -> None:
        """Test ReviewResult is immutable."""
        result = ReviewResult(
            review_mode="diff",
            commit_hash="a" * 40,
            branch_name="main",
            reviewed_at="2026-02-14T12:00:00Z",
            issues=[],
        )
        with pytest.raises(AttributeError):
            result.review_mode = "pr"  # type: ignore[misc]

    def test_invalid_review_mode_raises_error(self) -> None:
        """Test invalid review_mode raises ValueError."""
        with pytest.raises(ValueError, match="review_mode"):
            ReviewResult(
                review_mode="invalid",
                commit_hash="a" * 40,
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                issues=[],
            )

    def test_valid_review_modes(self) -> None:
        """Test both valid review_mode values are accepted."""
        for mode in ("diff", "pr"):
            result = ReviewResult(
                review_mode=mode,
                commit_hash="a" * 40,
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                issues=[],
            )
            assert result.review_mode == mode

    def test_invalid_commit_hash_length_raises_error(self) -> None:
        """Test commit_hash with wrong length raises ValueError."""
        with pytest.raises(ValueError, match="commit_hash"):
            ReviewResult(
                review_mode="diff",
                commit_hash="abc123",
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                issues=[],
            )

    def test_invalid_commit_hash_characters_raises_error(self) -> None:
        """Test commit_hash with non-hex characters raises ValueError."""
        with pytest.raises(ValueError, match="commit_hash"):
            ReviewResult(
                review_mode="diff",
                commit_hash="g" * 40,
                branch_name="main",
                reviewed_at="2026-02-14T12:00:00Z",
                issues=[],
            )
