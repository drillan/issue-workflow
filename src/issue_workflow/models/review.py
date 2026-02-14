"""Review result models for hachimoku integration."""

from dataclasses import dataclass
from enum import Enum


class ReviewMode(str, Enum):
    """Review mode for hachimoku."""

    DIFF = "diff"
    PR = "pr"


class AgentResultStatus(str, Enum):
    """Status of a review agent execution."""

    SUCCESS = "success"
    ERROR = "error"


class ReviewSeverity(str, Enum):
    """Review issue severity level."""

    CRITICAL = "Critical"
    IMPORTANT = "Important"
    SUGGESTION = "Suggestion"
    NITPICK = "Nitpick"


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
class ReviewAgentResult:
    """Result from a single hachimoku review agent."""

    status: AgentResultStatus
    agent_name: str
    issues: list[ReviewIssue]
    elapsed_time: float
    error_message: str | None = None


@dataclass(frozen=True)
class ReviewSummary:
    """Summary statistics from a hachimoku review session."""

    total_issues: int
    max_severity: ReviewSeverity | None
    total_elapsed_time: float


@dataclass(frozen=True)
class ReviewResult:
    """Review result from a hachimoku review session.

    Each instance represents one line in the JSONL output file.
    A review session contains results from multiple agents.
    """

    review_mode: ReviewMode
    commit_hash: str
    branch_name: str
    reviewed_at: str
    results: list[ReviewAgentResult]
    summary: ReviewSummary
    pr_number: int | None = None

    _COMMIT_HASH_LENGTH = 40
    _HEX_CHARS = frozenset("0123456789abcdef")

    def __post_init__(self) -> None:
        """Validate invariants after initialization."""
        if len(self.commit_hash) != self._COMMIT_HASH_LENGTH or not all(
            c in self._HEX_CHARS for c in self.commit_hash.lower()
        ):
            msg = f"commit_hash must be a 40-character hexadecimal string, got '{self.commit_hash}'"
            raise ValueError(msg)

    @property
    def all_issues(self) -> list[ReviewIssue]:
        """Flatten issues from all successful agent results."""
        return [
            issue
            for agent_result in self.results
            if agent_result.status == AgentResultStatus.SUCCESS
            for issue in agent_result.issues
        ]

    @property
    def has_critical(self) -> bool:
        """Whether any critical issues exist."""
        return any(issue.severity == ReviewSeverity.CRITICAL for issue in self.all_issues)
