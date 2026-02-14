"""Review result models for hachimoku integration."""

from dataclasses import dataclass
from enum import Enum


class ReviewSeverity(str, Enum):
    """Review issue severity level."""

    CRITICAL = "Critical"
    IMPORTANT = "Important"
    SUGGESTION = "Suggestion"


@dataclass(frozen=True)
class ReviewIssueLocation:
    """Location of a review issue in source code."""

    file_path: str
    line_number: int


@dataclass(frozen=True)
class ReviewIssue:
    """Individual review issue from hachimoku."""

    agent_name: str
    severity: ReviewSeverity
    description: str
    location: ReviewIssueLocation | None = None
    suggestion: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class ReviewResult:
    """Review result from hachimoku."""

    review_mode: str
    commit_hash: str
    branch_name: str
    reviewed_at: str
    issues: list[ReviewIssue]

    _VALID_REVIEW_MODES = frozenset({"diff", "pr"})
    _COMMIT_HASH_LENGTH = 40
    _HEX_CHARS = frozenset("0123456789abcdef")

    def __post_init__(self) -> None:
        """Validate invariants after initialization."""
        if self.review_mode not in self._VALID_REVIEW_MODES:
            msg = f"review_mode must be 'diff' or 'pr', got '{self.review_mode}'"
            raise ValueError(msg)
        if len(self.commit_hash) != self._COMMIT_HASH_LENGTH or not all(
            c in self._HEX_CHARS for c in self.commit_hash.lower()
        ):
            msg = f"commit_hash must be a 40-character hexadecimal string, got '{self.commit_hash}'"
            raise ValueError(msg)

    @property
    def issue_count(self) -> int:
        """Count of review issues."""
        return len(self.issues)

    @property
    def has_critical(self) -> bool:
        """Whether any critical issues exist."""
        return any(i.severity == ReviewSeverity.CRITICAL for i in self.issues)
