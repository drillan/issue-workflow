"""GitHub Pull Request models."""

from dataclasses import dataclass
from enum import Enum


class MergeStrategy(str, Enum):
    """PR merge strategies."""

    SQUASH = "squash"
    MERGE = "merge"
    REBASE = "rebase"


class MergeState(str, Enum):
    """PR mergeability states."""

    MERGEABLE = "MERGEABLE"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


class PRState(str, Enum):
    """PR states."""

    OPEN = "OPEN"
    MERGED = "MERGED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class PullRequest:
    """GitHub Pull Request information."""

    number: int
    title: str
    state: PRState
    mergeable: MergeState
    base_ref_name: str
    head_ref_name: str

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if self.number <= 0:
            raise ValueError(f"number must be positive, got {self.number}")

    @property
    def can_merge(self) -> bool:
        """Check if PR can be merged."""
        return self.state == PRState.OPEN and self.mergeable == MergeState.MERGEABLE

    @classmethod
    def from_gh_json(cls, data: dict[str, object]) -> "PullRequest":
        """Create PullRequest from gh CLI JSON output."""
        state_str = str(data.get("state", "OPEN")).upper()
        mergeable_str = str(data.get("mergeable", "UNKNOWN")).upper()

        try:
            state = PRState(state_str)
        except ValueError:
            state = PRState.OPEN

        try:
            mergeable = MergeState(mergeable_str)
        except ValueError:
            mergeable = MergeState.UNKNOWN

        number_val = data.get("number", 0)
        return cls(
            number=int(number_val) if isinstance(number_val, (int, str)) else 0,
            title=str(data.get("title", "")),
            state=state,
            mergeable=mergeable,
            base_ref_name=str(data.get("baseRefName", "main")),
            head_ref_name=str(data.get("headRefName", "")),
        )
