"""JSONL review loader for hachimoku review results."""

import json
from pathlib import Path

from issue_workflow.models.review import (
    ReviewAgentResult,
    ReviewIssue,
    ReviewIssueLocation,
    ReviewResult,
    ReviewSeverity,
    ReviewSummary,
)


class ReviewFileNotFoundError(FileNotFoundError):
    """Raised when a review JSONL file does not exist."""


class ReviewParseError(ValueError):
    """Raised when a JSONL line cannot be parsed."""


def resolve_review_path(
    reviews_dir: Path,
    *,
    pr_number: int | None = None,
    diff: bool = False,
) -> Path:
    """Resolve the JSONL file path based on review mode.

    Args:
        reviews_dir: Path to .hachimoku/reviews/ directory.
        pr_number: PR number for PR mode.
        diff: If True, resolve diff mode file.

    Returns:
        Path to the JSONL file (not guaranteed to exist).

    Raises:
        ValueError: If neither pr_number nor diff is specified.
    """
    if pr_number is not None:
        return reviews_dir / f"pr-{pr_number}.jsonl"
    if diff:
        return reviews_dir / "diff.jsonl"
    msg = "Either pr_number or diff must be specified"
    raise ValueError(msg)


def load_reviews(jsonl_path: Path) -> list[ReviewResult]:
    """Load review results from a hachimoku JSONL file.

    Each line in the JSONL file represents one review session.

    Args:
        jsonl_path: Path to the JSONL file.

    Returns:
        List of ReviewResult objects, one per JSONL line.

    Raises:
        ReviewFileNotFoundError: If the JSONL file does not exist.
        ReviewParseError: If a line cannot be parsed as valid JSON.
    """
    if not jsonl_path.exists():
        msg = f"Review file not found: {jsonl_path.name}"
        raise ReviewFileNotFoundError(msg)

    results: list[ReviewResult] = []
    for line_number, line in enumerate(jsonl_path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSONL at line {line_number}: {e}"
            raise ReviewParseError(msg) from e

        results.append(_parse_review_result(data))

    return results


def _parse_review_result(data: dict[str, object]) -> ReviewResult:
    """Parse a single JSONL line into a ReviewResult."""
    raw_results = data.get("results", [])
    assert isinstance(raw_results, list)

    agent_results = [_parse_agent_result(r) for r in raw_results]

    raw_summary = data.get("summary", {})
    assert isinstance(raw_summary, dict)
    summary = _parse_summary(raw_summary)

    pr_number_raw = data.get("pr_number")
    pr_number: int | None = None
    if isinstance(pr_number_raw, (int, float)):
        pr_number = int(pr_number_raw)

    return ReviewResult(
        review_mode=str(data["review_mode"]),
        commit_hash=str(data["commit_hash"]),
        branch_name=str(data["branch_name"]),
        reviewed_at=str(data["reviewed_at"]),
        results=agent_results,
        summary=summary,
        pr_number=pr_number,
    )


def _parse_agent_result(data: dict[str, object]) -> ReviewAgentResult:
    """Parse an agent result from JSONL data."""
    raw_issues = data.get("issues", [])
    assert isinstance(raw_issues, list)

    issues = [_parse_issue(i) for i in raw_issues]

    return ReviewAgentResult(
        status=str(data["status"]),
        agent_name=str(data["agent_name"]),
        issues=issues,
        elapsed_time=float(str(data.get("elapsed_time", 0))),
        error_message=str(data["error_message"]) if data.get("error_message") else None,
    )


def _parse_issue(data: dict[str, object]) -> ReviewIssue:
    """Parse a single review issue from JSONL data."""
    location = None
    raw_location = data.get("location")
    if isinstance(raw_location, dict):
        location = ReviewIssueLocation(
            file_path=str(raw_location["file_path"]),
            line_number=int(str(raw_location["line_number"])),
        )

    return ReviewIssue(
        agent_name=str(data["agent_name"]),
        severity=ReviewSeverity(str(data["severity"])),
        description=str(data["description"]),
        location=location,
        suggestion=str(data["suggestion"]) if data.get("suggestion") else None,
        category=str(data["category"]) if data.get("category") else None,
    )


def _parse_summary(data: dict[str, object]) -> ReviewSummary:
    """Parse the review summary from JSONL data."""
    max_severity_raw = data.get("max_severity")
    max_severity = ReviewSeverity(str(max_severity_raw)) if max_severity_raw is not None else None

    return ReviewSummary(
        total_issues=int(str(data.get("total_issues", 0))),
        max_severity=max_severity,
        total_elapsed_time=float(str(data.get("total_elapsed_time", 0))),
    )
