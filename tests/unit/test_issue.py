"""Unit tests for Issue model."""

import pytest

from issue_workflow.models.issue import Issue, IssueState


class TestIssueState:
    """Tests for IssueState enum."""

    def test_issue_state_values(self) -> None:
        """Test IssueState has expected values."""
        assert IssueState.OPEN.value == "OPEN"
        assert IssueState.CLOSED.value == "CLOSED"

    def test_issue_state_is_str_enum(self) -> None:
        """Test IssueState can be used as string."""
        assert IssueState.OPEN == "OPEN"
        assert IssueState.CLOSED == "CLOSED"

    def test_issue_state_from_string(self) -> None:
        """Test IssueState can be created from string."""
        assert IssueState("OPEN") == IssueState.OPEN
        assert IssueState("CLOSED") == IssueState.CLOSED

    def test_issue_state_invalid_value(self) -> None:
        """Test invalid state value raises error."""
        with pytest.raises(ValueError):
            IssueState("INVALID")


class TestIssueValidation:
    """Tests for Issue field validation."""

    def test_number_must_be_positive(self) -> None:
        """Test number rejects zero."""
        with pytest.raises(ValueError, match="number must be positive"):
            Issue(
                number=0,
                title="Test",
                body="",
                labels=[],
                state=IssueState.OPEN,
            )

    def test_number_rejects_negative(self) -> None:
        """Test number rejects negative values."""
        with pytest.raises(ValueError, match="number must be positive"):
            Issue(
                number=-1,
                title="Test",
                body="",
                labels=[],
                state=IssueState.OPEN,
            )

    def test_number_accepts_positive(self) -> None:
        """Test number accepts positive values."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state=IssueState.OPEN,
        )
        assert issue.number == 1


class TestIssueModel:
    """Tests for Issue dataclass."""

    def test_create_issue(self) -> None:
        """Test creating an issue."""
        issue = Issue(
            number=123,
            title="Test Issue",
            body="Test body content",
            labels=["bug", "enhancement"],
            state=IssueState.OPEN,
        )
        assert issue.number == 123
        assert issue.title == "Test Issue"
        assert issue.body == "Test body content"
        assert issue.labels == ["bug", "enhancement"]
        assert issue.state == IssueState.OPEN

    def test_is_open_true(self) -> None:
        """Test is_open property returns True for open issues."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state=IssueState.OPEN,
        )
        assert issue.is_open is True

    def test_is_open_false(self) -> None:
        """Test is_open property returns False for closed issues."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state=IssueState.CLOSED,
        )
        assert issue.is_open is False

    def test_issue_is_frozen(self) -> None:
        """Test issue is immutable."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state=IssueState.OPEN,
        )
        with pytest.raises(AttributeError):
            issue.number = 2  # type: ignore[misc]


class TestIssueFromGhJson:
    """Tests for Issue.from_gh_json class method."""

    def test_from_gh_json_basic(self) -> None:
        """Test creating issue from basic gh JSON."""
        data = {
            "number": 123,
            "title": "Test Issue",
            "body": "Test body",
            "labels": [{"name": "bug"}],
            "state": "OPEN",
        }
        issue = Issue.from_gh_json(data)
        assert issue.number == 123
        assert issue.title == "Test Issue"
        assert issue.body == "Test body"
        assert issue.labels == ["bug"]
        assert issue.state == IssueState.OPEN

    def test_from_gh_json_multiple_labels(self) -> None:
        """Test creating issue with multiple labels."""
        data = {
            "number": 456,
            "title": "Multi-label Issue",
            "body": "",
            "labels": [{"name": "bug"}, {"name": "urgent"}, {"name": "frontend"}],
            "state": "OPEN",
        }
        issue = Issue.from_gh_json(data)
        assert issue.labels == ["bug", "urgent", "frontend"]

    def test_from_gh_json_empty_labels(self) -> None:
        """Test creating issue with empty labels."""
        data = {
            "number": 789,
            "title": "No Labels",
            "body": "",
            "labels": [],
            "state": "OPEN",
        }
        issue = Issue.from_gh_json(data)
        assert issue.labels == []

    def test_from_gh_json_missing_fields(self) -> None:
        """Test creating issue with missing fields uses defaults."""
        data: dict[str, object] = {"number": 1}
        issue = Issue.from_gh_json(data)
        assert issue.number == 1
        assert issue.title == ""
        assert issue.body == ""
        assert issue.labels == []
        assert issue.state == IssueState.OPEN

    def test_from_gh_json_string_labels(self) -> None:
        """Test creating issue with string labels (edge case)."""
        data = {
            "number": 1,
            "title": "Test",
            "body": "",
            "labels": ["bug", "feature"],  # String labels instead of dicts
            "state": "OPEN",
        }
        issue = Issue.from_gh_json(data)
        assert issue.labels == ["bug", "feature"]

    def test_from_gh_json_missing_number_raises_error(self) -> None:
        """Test creating issue without number raises ValueError."""
        data: dict[str, object] = {"title": "Test"}
        with pytest.raises(ValueError, match="number must be positive"):
            Issue.from_gh_json(data)
