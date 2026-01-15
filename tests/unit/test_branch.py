"""Unit tests for branch type detection and naming."""

from typing import Protocol

import pytest

from issue_workflow.models.branch import Branch, BranchType
from issue_workflow.models.issue import Issue, IssueState


class IssueFactory(Protocol):
    """Protocol for issue factory fixture."""

    @staticmethod
    def with_labels(labels: tuple[str, ...], title: str = "Test Issue") -> Issue: ...

    @staticmethod
    def with_title(title: str, labels: tuple[str, ...] | None = None) -> Issue: ...


class TestBranchTypeDetection:
    """Tests for branch type detection from labels/keywords."""

    @pytest.fixture
    def create_issue(self) -> type[IssueFactory]:
        """Factory for creating test issues."""

        class Factory:
            @staticmethod
            def with_labels(labels: tuple[str, ...], title: str = "Sample Issue") -> Issue:
                return Issue(
                    number=123,
                    title=title,
                    body="Sample body",
                    labels=labels,
                    state=IssueState.OPEN,
                )

            @staticmethod
            def with_title(title: str, labels: tuple[str, ...] | None = None) -> Issue:
                return Issue(
                    number=123,
                    title=title,
                    body="",
                    labels=labels or (),
                    state=IssueState.OPEN,
                )

        return Factory

    def test_enhancement_label_maps_to_feat(self, create_issue: type[IssueFactory]) -> None:
        """Test enhancement label maps to feat prefix."""
        issue = create_issue.with_labels(("enhancement",))
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.FEAT

    def test_bug_label_maps_to_fix(self, create_issue: type[IssueFactory]) -> None:
        """Test bug label maps to fix prefix."""
        issue = create_issue.with_labels(("bug",))
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.FIX

    def test_refactoring_label_maps_to_refactor(self, create_issue: type[IssueFactory]) -> None:
        """Test refactoring label maps to refactor prefix."""
        issue = create_issue.with_labels(("refactoring",))
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.REFACTOR

    def test_documentation_label_maps_to_docs(self, create_issue: type[IssueFactory]) -> None:
        """Test documentation label maps to docs prefix."""
        issue = create_issue.with_labels(("documentation",))
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.DOCS

    def test_fix_keyword_in_title(self, create_issue: type[IssueFactory]) -> None:
        """Test fix keyword in title maps to fix prefix."""
        issue = create_issue.with_title("Fix login error")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.FIX

    def test_add_keyword_in_title(self, create_issue: type[IssueFactory]) -> None:
        """Test add keyword in title maps to feat prefix."""
        issue = create_issue.with_title("Add user authentication")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.FEAT

    def test_refactor_keyword_in_title(self, create_issue: type[IssueFactory]) -> None:
        """Test refactor keyword in title maps to refactor prefix."""
        issue = create_issue.with_title("Refactor authentication module")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.REFACTOR

    def test_doc_keyword_in_title(self, create_issue: type[IssueFactory]) -> None:
        """Test doc keyword in title maps to docs prefix."""
        issue = create_issue.with_title("Update doc for API endpoints")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.DOCS

    def test_test_keyword_in_title(self, create_issue: type[IssueFactory]) -> None:
        """Test test keyword in title maps to test prefix."""
        issue = create_issue.with_title("Add test for user service")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.TEST

    def test_chore_keyword_in_title(self, create_issue: type[IssueFactory]) -> None:
        """Test chore keyword in title maps to chore prefix."""
        issue = create_issue.with_title("Chore: update dependencies")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.CHORE

    def test_default_to_feat(self, create_issue: type[IssueFactory]) -> None:
        """Test default branch type is feat."""
        # Use a title without keywords to ensure default
        issue = create_issue.with_labels((), title="Something unrelated")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.FEAT

    def test_label_takes_precedence_over_keyword(self, create_issue: type[IssueFactory]) -> None:
        """Test that label takes precedence over keyword in title."""
        issue = create_issue.with_labels(("enhancement",), title="Fix something")
        from issue_workflow.services.branch import detect_branch_type

        assert detect_branch_type(issue) == BranchType.FEAT


class TestBranchValidation:
    """Tests for Branch field validation."""

    def test_issue_number_must_be_positive(self) -> None:
        """Test issue_number rejects zero."""
        with pytest.raises(ValueError, match="issue_number must be positive"):
            Branch(type=BranchType.FEAT, issue_number=0, description="test")

    def test_issue_number_rejects_negative(self) -> None:
        """Test issue_number rejects negative values."""
        with pytest.raises(ValueError, match="issue_number must be positive"):
            Branch(type=BranchType.FEAT, issue_number=-1, description="test")

    def test_issue_number_accepts_positive(self) -> None:
        """Test issue_number accepts positive values."""
        branch = Branch(type=BranchType.FEAT, issue_number=1, description="test")
        assert branch.issue_number == 1


class TestBranchNaming:
    """Tests for branch name generation."""

    def test_normalize_description_lowercase(self) -> None:
        """Test description is converted to lowercase."""
        result = Branch._normalize_description("Add User Authentication")
        assert result == "add-user-authentication"

    def test_normalize_description_special_chars_removed(self) -> None:
        """Test special characters are removed."""
        result = Branch._normalize_description("Fix bug: login fails!")
        assert result == "fix-bug-login-fails"

    def test_normalize_description_spaces_to_hyphens(self) -> None:
        """Test spaces are converted to hyphens."""
        result = Branch._normalize_description("add new feature")
        assert result == "add-new-feature"

    def test_normalize_description_max_length(self) -> None:
        """Test description is limited to max length."""
        long_title = "This is a very long title that should be truncated at word boundary"
        result = Branch._normalize_description(long_title, max_length=40)
        assert len(result) <= 40

    def test_branch_name_format(self) -> None:
        """Test branch name follows format: type/number-description."""
        branch = Branch(
            type=BranchType.FEAT,
            issue_number=123,
            description="add-auth",
        )
        assert branch.name == "feat/123-add-auth"

    def test_from_issue(self) -> None:
        """Test branch creation from issue."""
        issue = Issue(
            number=456,
            title="Add user login",
            body="",
            labels=("enhancement",),
            state=IssueState.OPEN,
        )
        branch = Branch.from_issue(issue, BranchType.FEAT)
        assert branch.issue_number == 456
        assert branch.type == BranchType.FEAT
        assert "add-user-login" in branch.name


class TestBranchIssueExtraction:
    """Tests for extracting issue number from branch name."""

    def test_extract_feat_branch(self) -> None:
        """Test extracting issue from feat branch."""
        result = Branch.extract_issue_number("feat/123-add-feature")
        assert result == 123

    def test_extract_fix_branch(self) -> None:
        """Test extracting issue from fix branch."""
        result = Branch.extract_issue_number("fix/456-fix-bug")
        assert result == 456

    def test_extract_feature_branch_legacy(self) -> None:
        """Test extracting issue from legacy feature branch."""
        result = Branch.extract_issue_number("feature/789-add-feature")
        assert result == 789

    def test_extract_bugfix_branch_legacy(self) -> None:
        """Test extracting issue from legacy bugfix branch."""
        result = Branch.extract_issue_number("bugfix/101-fix-issue")
        assert result == 101

    def test_invalid_branch_returns_none(self) -> None:
        """Test invalid branch name returns None."""
        result = Branch.extract_issue_number("main")
        assert result is None

    def test_branch_without_issue_number(self) -> None:
        """Test branch without issue number returns None."""
        result = Branch.extract_issue_number("feat/add-feature")
        assert result is None
