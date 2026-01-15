"""Unit tests for PullRequest model."""

import pytest

from issue_workflow.models.pr import MergeState, MergeStrategy, PRState, PullRequest


class TestPullRequestValidation:
    """Tests for PullRequest field validation."""

    def test_number_must_be_positive(self) -> None:
        """Test number rejects zero."""
        with pytest.raises(ValueError, match="number must be positive"):
            PullRequest(
                number=0,
                title="Test",
                state=PRState.OPEN,
                mergeable=MergeState.MERGEABLE,
                base_ref_name="main",
                head_ref_name="feat/1-test",
            )

    def test_number_rejects_negative(self) -> None:
        """Test number rejects negative values."""
        with pytest.raises(ValueError, match="number must be positive"):
            PullRequest(
                number=-1,
                title="Test",
                state=PRState.OPEN,
                mergeable=MergeState.MERGEABLE,
                base_ref_name="main",
                head_ref_name="feat/1-test",
            )

    def test_number_accepts_positive(self) -> None:
        """Test number accepts positive values."""
        pr = PullRequest(
            number=1,
            title="Test",
            state=PRState.OPEN,
            mergeable=MergeState.MERGEABLE,
            base_ref_name="main",
            head_ref_name="feat/1-test",
        )
        assert pr.number == 1


class TestPullRequestModel:
    """Tests for PullRequest dataclass."""

    def test_create_pull_request(self) -> None:
        """Test creating a pull request."""
        pr = PullRequest(
            number=100,
            title="Add feature",
            state=PRState.OPEN,
            mergeable=MergeState.MERGEABLE,
            base_ref_name="main",
            head_ref_name="feat/123-add-feature",
        )
        assert pr.number == 100
        assert pr.title == "Add feature"
        assert pr.state == PRState.OPEN
        assert pr.mergeable == MergeState.MERGEABLE

    def test_can_merge_open_and_mergeable(self) -> None:
        """Test can_merge returns True for open and mergeable PR."""
        pr = PullRequest(
            number=1,
            title="Test",
            state=PRState.OPEN,
            mergeable=MergeState.MERGEABLE,
            base_ref_name="main",
            head_ref_name="feat/1-test",
        )
        assert pr.can_merge is True

    def test_can_merge_conflicting(self) -> None:
        """Test can_merge returns False for conflicting PR."""
        pr = PullRequest(
            number=1,
            title="Test",
            state=PRState.OPEN,
            mergeable=MergeState.CONFLICTING,
            base_ref_name="main",
            head_ref_name="feat/1-test",
        )
        assert pr.can_merge is False

    def test_can_merge_already_merged(self) -> None:
        """Test can_merge returns False for already merged PR."""
        pr = PullRequest(
            number=1,
            title="Test",
            state=PRState.MERGED,
            mergeable=MergeState.MERGEABLE,
            base_ref_name="main",
            head_ref_name="feat/1-test",
        )
        assert pr.can_merge is False

    def test_can_merge_closed(self) -> None:
        """Test can_merge returns False for closed PR."""
        pr = PullRequest(
            number=1,
            title="Test",
            state=PRState.CLOSED,
            mergeable=MergeState.MERGEABLE,
            base_ref_name="main",
            head_ref_name="feat/1-test",
        )
        assert pr.can_merge is False

    def test_pr_is_frozen(self) -> None:
        """Test PR is immutable."""
        pr = PullRequest(
            number=1,
            title="Test",
            state=PRState.OPEN,
            mergeable=MergeState.MERGEABLE,
            base_ref_name="main",
            head_ref_name="feat/1-test",
        )
        with pytest.raises(AttributeError):
            pr.number = 2  # type: ignore[misc]


class TestPullRequestFromGhJson:
    """Tests for PullRequest.from_gh_json class method."""

    def test_from_gh_json_basic(self) -> None:
        """Test creating PR from basic gh JSON."""
        data = {
            "number": 100,
            "title": "Test PR",
            "state": "OPEN",
            "mergeable": "MERGEABLE",
            "baseRefName": "main",
            "headRefName": "feat/123-test",
        }
        pr = PullRequest.from_gh_json(data)
        assert pr.number == 100
        assert pr.title == "Test PR"
        assert pr.state == PRState.OPEN
        assert pr.mergeable == MergeState.MERGEABLE
        assert pr.base_ref_name == "main"
        assert pr.head_ref_name == "feat/123-test"

    def test_from_gh_json_merged(self) -> None:
        """Test creating merged PR from gh JSON."""
        data = {
            "number": 200,
            "title": "Merged PR",
            "state": "MERGED",
            "mergeable": "UNKNOWN",
            "baseRefName": "main",
            "headRefName": "feat/200-merged",
        }
        pr = PullRequest.from_gh_json(data)
        assert pr.state == PRState.MERGED

    def test_from_gh_json_invalid_state_raises_valueerror(self) -> None:
        """Test invalid state raises ValueError."""
        data = {
            "number": 1,
            "title": "Test",
            "state": "INVALID_STATE",
            "mergeable": "MERGEABLE",
            "baseRefName": "main",
            "headRefName": "test",
        }
        with pytest.raises(ValueError, match="'INVALID_STATE' is not a valid PRState"):
            PullRequest.from_gh_json(data)

    def test_from_gh_json_invalid_mergeable_raises_valueerror(self) -> None:
        """Test invalid mergeable raises ValueError."""
        data = {
            "number": 1,
            "title": "Test",
            "state": "OPEN",
            "mergeable": "INVALID",
            "baseRefName": "main",
            "headRefName": "test",
        }
        with pytest.raises(ValueError, match="'INVALID' is not a valid MergeState"):
            PullRequest.from_gh_json(data)

    def test_from_gh_json_missing_number_raises_keyerror(self) -> None:
        """Test missing number raises KeyError."""
        data: dict[str, object] = {
            "title": "Test",
            "state": "OPEN",
            "mergeable": "MERGEABLE",
            "baseRefName": "main",
            "headRefName": "test",
        }
        with pytest.raises(KeyError):
            PullRequest.from_gh_json(data)


class TestMergeStrategy:
    """Tests for MergeStrategy enum."""

    def test_merge_strategies(self) -> None:
        """Test all merge strategies are defined."""
        assert MergeStrategy.SQUASH.value == "squash"
        assert MergeStrategy.MERGE.value == "merge"
        assert MergeStrategy.REBASE.value == "rebase"
