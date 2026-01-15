"""Unit tests for Issue model."""

import pytest

from issue_workflow.models.issue import Issue


class TestIssueModel:
    """Tests for Issue dataclass."""

    def test_create_issue(self) -> None:
        """Test creating an issue."""
        issue = Issue(
            number=123,
            title="Test Issue",
            body="Test body content",
            labels=["bug", "enhancement"],
            state="OPEN",
        )
        assert issue.number == 123
        assert issue.title == "Test Issue"
        assert issue.body == "Test body content"
        assert issue.labels == ["bug", "enhancement"]
        assert issue.state == "OPEN"

    def test_is_open_true(self) -> None:
        """Test is_open property returns True for open issues."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state="OPEN",
        )
        assert issue.is_open is True

    def test_is_open_false(self) -> None:
        """Test is_open property returns False for closed issues."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state="CLOSED",
        )
        assert issue.is_open is False

    def test_issue_is_frozen(self) -> None:
        """Test issue is immutable."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            labels=[],
            state="OPEN",
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
        assert issue.state == "OPEN"

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
        assert issue.state == "OPEN"

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
