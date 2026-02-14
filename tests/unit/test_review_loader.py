"""Unit tests for JSONL review loader service."""

import json
from pathlib import Path

import pytest

from issue_workflow.models.review import (
    AgentResultStatus,
    ReviewMode,
    ReviewSeverity,
)
from issue_workflow.services.review_loader import (
    ReviewFileNotFoundError,
    ReviewParseError,
    load_reviews,
    resolve_review_path,
)


@pytest.fixture()
def reviews_dir(tmp_path: Path) -> Path:
    """Create a temporary reviews directory."""
    review_dir = tmp_path / ".hachimoku" / "reviews"
    review_dir.mkdir(parents=True)
    return review_dir


@pytest.fixture()
def sample_review_line() -> dict[str, object]:
    """A minimal valid JSONL line matching hachimoku output."""
    return {
        "review_mode": "diff",
        "commit_hash": "a" * 40,
        "branch_name": "feat/42-some-feature",
        "reviewed_at": "2026-02-14T12:00:00Z",
        "results": [
            {
                "status": "success",
                "agent_name": "code-reviewer",
                "issues": [
                    {
                        "agent_name": "code-reviewer",
                        "severity": "Important",
                        "description": "Missing error handling",
                        "location": {
                            "file_path": "src/main.py",
                            "line_number": 28,
                        },
                        "suggestion": "Add try/except block",
                        "category": "bug",
                    },
                    {
                        "agent_name": "code-reviewer",
                        "severity": "Suggestion",
                        "description": "Consider renaming",
                        "location": None,
                        "suggestion": None,
                        "category": None,
                    },
                ],
                "elapsed_time": 109.5,
                "cost": {
                    "input_tokens": 13,
                    "output_tokens": 2667,
                    "total_cost": None,
                },
            }
        ],
        "summary": {
            "total_issues": 2,
            "max_severity": "Important",
            "total_elapsed_time": 109.5,
            "total_cost": {
                "input_tokens": 13,
                "output_tokens": 2667,
                "total_cost": None,
            },
        },
    }


@pytest.fixture()
def pr_review_line() -> dict[str, object]:
    """A valid JSONL line for PR mode."""
    return {
        "review_mode": "pr",
        "commit_hash": "b" * 40,
        "pr_number": 210,
        "branch_name": "docs/207-uv-tool-install-guide",
        "reviewed_at": "2026-02-13T10:14:33.960289Z",
        "results": [
            {
                "status": "success",
                "agent_name": "code-reviewer",
                "issues": [],
                "elapsed_time": 89.9,
                "cost": {
                    "input_tokens": 3116,
                    "output_tokens": 1778,
                    "total_cost": None,
                },
            }
        ],
        "summary": {
            "total_issues": 0,
            "max_severity": None,
            "total_elapsed_time": 89.9,
            "total_cost": {
                "input_tokens": 3116,
                "output_tokens": 1778,
                "total_cost": None,
            },
        },
    }


@pytest.fixture()
def error_result_line() -> dict[str, object]:
    """A JSONL line containing an error agent result."""
    return {
        "review_mode": "diff",
        "commit_hash": "c" * 40,
        "branch_name": "feat/32-test",
        "reviewed_at": "2026-02-14T01:23:38Z",
        "results": [
            {
                "status": "success",
                "agent_name": "code-reviewer",
                "issues": [
                    {
                        "agent_name": "code-reviewer",
                        "severity": "Important",
                        "description": "Found a bug",
                        "location": {"file_path": "src/app.py", "line_number": 10},
                        "suggestion": "Fix the bug",
                        "category": "bug",
                    },
                ],
                "elapsed_time": 100.0,
                "cost": {"input_tokens": 10, "output_tokens": 500, "total_cost": None},
            },
            {
                "status": "error",
                "agent_name": "pr-test-analyzer",
                "error_message": "Structured output recovery failed",
                "exit_code": None,
                "error_type": None,
                "stderr": None,
                "issues": [],
                "elapsed_time": 156.0,
                "cost": {"input_tokens": 0, "output_tokens": 0, "total_cost": None},
            },
        ],
        "summary": {
            "total_issues": 1,
            "max_severity": "Important",
            "total_elapsed_time": 256.0,
            "total_cost": {"input_tokens": 10, "output_tokens": 500, "total_cost": None},
        },
    }


class TestResolveReviewPath:
    """Tests for resolve_review_path."""

    def test_pr_mode(self, reviews_dir: Path) -> None:
        expected = reviews_dir / "pr-210.jsonl"
        assert resolve_review_path(reviews_dir, pr_number=210) == expected

    def test_diff_mode(self, reviews_dir: Path) -> None:
        expected = reviews_dir / "diff.jsonl"
        assert resolve_review_path(reviews_dir, diff=True) == expected

    def test_pr_number_takes_precedence_over_diff(self, reviews_dir: Path) -> None:
        expected = reviews_dir / "pr-100.jsonl"
        assert resolve_review_path(reviews_dir, pr_number=100, diff=True) == expected

    def test_no_args_raises_error(self, reviews_dir: Path) -> None:
        with pytest.raises(ValueError, match="pr_number or diff"):
            resolve_review_path(reviews_dir)


class TestLoadReviews:
    """Tests for load_reviews."""

    def test_load_single_line(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        results = load_reviews(jsonl_path)
        assert len(results) == 1
        assert results[0].review_mode == ReviewMode.DIFF
        assert results[0].commit_hash == "a" * 40
        assert results[0].summary.total_issues == 2
        assert len(results[0].results) == 1
        assert len(results[0].all_issues) == 2

    def test_load_multiple_lines(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
        pr_review_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        lines = [json.dumps(sample_review_line), json.dumps(pr_review_line)]
        jsonl_path.write_text("\n".join(lines) + "\n")

        results = load_reviews(jsonl_path)
        assert len(results) == 2

    def test_load_pr_mode_with_pr_number(
        self,
        reviews_dir: Path,
        pr_review_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "pr-210.jsonl"
        jsonl_path.write_text(json.dumps(pr_review_line) + "\n")

        results = load_reviews(jsonl_path)
        assert len(results) == 1
        assert results[0].review_mode == ReviewMode.PR
        assert results[0].pr_number == 210

    def test_load_with_error_agent(
        self,
        reviews_dir: Path,
        error_result_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(error_result_line) + "\n")

        results = load_reviews(jsonl_path)
        assert len(results) == 1
        assert len(results[0].results) == 2
        assert results[0].results[0].status == AgentResultStatus.SUCCESS
        assert results[0].results[1].status == AgentResultStatus.ERROR
        assert results[0].results[1].error_message == "Structured output recovery failed"
        # all_issues should only include successful agent results
        assert len(results[0].all_issues) == 1

    def test_issue_fields_parsed_correctly(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        results = load_reviews(jsonl_path)
        issues = results[0].all_issues
        assert issues[0].severity == ReviewSeverity.IMPORTANT
        assert issues[0].description == "Missing error handling"
        assert issues[0].location is not None
        assert issues[0].location.file_path == "src/main.py"
        assert issues[0].location.line_number == 28
        assert issues[0].suggestion == "Add try/except block"
        assert issues[0].category == "bug"

    def test_issue_with_null_optional_fields(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        results = load_reviews(jsonl_path)
        issues = results[0].all_issues
        assert issues[1].location is None
        assert issues[1].suggestion is None
        assert issues[1].category is None

    def test_file_not_found_raises_error(self, reviews_dir: Path) -> None:
        nonexistent = reviews_dir / "pr-999.jsonl"
        with pytest.raises(ReviewFileNotFoundError, match=r"pr-999\.jsonl"):
            load_reviews(nonexistent)

    def test_invalid_json_raises_parse_error(self, reviews_dir: Path) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text("not valid json\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)

    def test_empty_file_returns_empty_list(self, reviews_dir: Path) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text("")

        results = load_reviews(jsonl_path)
        assert results == []

    def test_skips_blank_lines(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        jsonl_path = reviews_dir / "diff.jsonl"
        content = f"\n{json.dumps(sample_review_line)}\n\n"
        jsonl_path.write_text(content)

        results = load_reviews(jsonl_path)
        assert len(results) == 1

    def test_loads_latest_review(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        """Last line in JSONL is the latest review session."""
        jsonl_path = reviews_dir / "diff.jsonl"
        lines = [json.dumps(sample_review_line), json.dumps(sample_review_line)]
        jsonl_path.write_text("\n".join(lines) + "\n")

        results = load_reviews(jsonl_path)
        assert len(results) == 2
        # The function returns all results; caller decides which to use

    def test_missing_results_field_raises_parse_error(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        """Missing required 'results' field should raise ReviewParseError."""
        del sample_review_line["results"]
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)

    def test_missing_summary_field_raises_parse_error(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        """Missing required 'summary' field should raise ReviewParseError."""
        del sample_review_line["summary"]
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)

    def test_missing_review_mode_raises_parse_error(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        """Missing required 'review_mode' field should raise ReviewParseError."""
        del sample_review_line["review_mode"]
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)

    def test_results_not_a_list_raises_parse_error(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        """'results' as a string instead of list should raise ReviewParseError."""
        sample_review_line["results"] = "not-a-list"
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        with pytest.raises(ReviewParseError, match="list"):
            load_reviews(jsonl_path)

    def test_summary_not_a_dict_raises_parse_error(
        self,
        reviews_dir: Path,
        sample_review_line: dict[str, object],
    ) -> None:
        """'summary' as a list instead of dict should raise ReviewParseError."""
        sample_review_line["summary"] = ["not-a-dict"]
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(sample_review_line) + "\n")

        with pytest.raises(ReviewParseError, match="dict"):
            load_reviews(jsonl_path)

    def test_issues_not_a_list_raises_parse_error(
        self,
        reviews_dir: Path,
    ) -> None:
        """'issues' as a string inside agent result should raise ReviewParseError."""
        data = {
            "review_mode": "diff",
            "commit_hash": "a" * 40,
            "branch_name": "main",
            "reviewed_at": "2026-02-14T12:00:00Z",
            "results": [
                {
                    "status": "success",
                    "agent_name": "code-reviewer",
                    "issues": "not-a-list",
                    "elapsed_time": 10.0,
                }
            ],
            "summary": {
                "total_issues": 0,
                "max_severity": None,
                "total_elapsed_time": 10.0,
            },
        }
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(data) + "\n")

        with pytest.raises(ReviewParseError, match="list"):
            load_reviews(jsonl_path)

    def test_invalid_severity_raises_parse_error(
        self,
        reviews_dir: Path,
    ) -> None:
        """Invalid severity value should raise ReviewParseError."""
        data = {
            "review_mode": "diff",
            "commit_hash": "a" * 40,
            "branch_name": "main",
            "reviewed_at": "2026-02-14T12:00:00Z",
            "results": [
                {
                    "status": "success",
                    "agent_name": "code-reviewer",
                    "issues": [
                        {
                            "agent_name": "code-reviewer",
                            "severity": "InvalidSeverity",
                            "description": "test",
                        }
                    ],
                    "elapsed_time": 10.0,
                }
            ],
            "summary": {
                "total_issues": 1,
                "max_severity": "InvalidSeverity",
                "total_elapsed_time": 10.0,
            },
        }
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(data) + "\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)

    def test_invalid_review_mode_raises_parse_error(
        self,
        reviews_dir: Path,
    ) -> None:
        """Invalid review_mode value should raise ReviewParseError."""
        data = {
            "review_mode": "unknown",
            "commit_hash": "a" * 40,
            "branch_name": "main",
            "reviewed_at": "2026-02-14T12:00:00Z",
            "results": [],
            "summary": {
                "total_issues": 0,
                "max_severity": None,
                "total_elapsed_time": 0.0,
            },
        }
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(data) + "\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)

    def test_invalid_agent_status_raises_parse_error(
        self,
        reviews_dir: Path,
    ) -> None:
        """Invalid agent status value should raise ReviewParseError."""
        data = {
            "review_mode": "diff",
            "commit_hash": "a" * 40,
            "branch_name": "main",
            "reviewed_at": "2026-02-14T12:00:00Z",
            "results": [
                {
                    "status": "unknown_status",
                    "agent_name": "code-reviewer",
                    "issues": [],
                    "elapsed_time": 10.0,
                }
            ],
            "summary": {
                "total_issues": 0,
                "max_severity": None,
                "total_elapsed_time": 10.0,
            },
        }
        jsonl_path = reviews_dir / "diff.jsonl"
        jsonl_path.write_text(json.dumps(data) + "\n")

        with pytest.raises(ReviewParseError, match="line 1"):
            load_reviews(jsonl_path)
