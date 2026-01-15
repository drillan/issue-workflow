"""GitHub Issue model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    """GitHub Issue information."""

    number: int
    title: str
    body: str
    labels: list[str]
    state: str  # OPEN, CLOSED

    @property
    def is_open(self) -> bool:
        """Check if issue is open."""
        return self.state == "OPEN"

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
        return cls(
            number=int(number_val) if isinstance(number_val, (int, str)) else 0,
            title=str(data.get("title", "")),
            body=str(data.get("body", "")),
            labels=labels,
            state=str(data.get("state", "OPEN")),
        )
