"""GitHub Issue model."""

from dataclasses import dataclass
from enum import Enum


class IssueState(str, Enum):
    """Issue states."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class Issue:
    """GitHub Issue information."""

    number: int
    title: str
    body: str
    labels: list[str]
    state: IssueState

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if self.number <= 0:
            raise ValueError(f"number must be positive, got {self.number}")

    @property
    def is_open(self) -> bool:
        """Check if issue is open."""
        return self.state == IssueState.OPEN

    @classmethod
    def from_gh_json(cls, data: dict[str, object]) -> "Issue":
        """Create Issue from gh CLI JSON output."""
        labels_data = data.get("labels", [])
        if isinstance(labels_data, list):
            labels = [
                label.get("name", "") if isinstance(label, dict) else str(label)
                for label in labels_data
            ]
        else:
            labels = []

        number_val = data.get("number", 0)
        state_str = str(data.get("state", "OPEN"))
        try:
            state = IssueState(state_str)
        except ValueError:
            state = IssueState.OPEN
        return cls(
            number=int(number_val) if isinstance(number_val, (int, str)) else 0,
            title=str(data.get("title", "")),
            body=str(data.get("body", "")),
            labels=labels,
            state=state,
        )
