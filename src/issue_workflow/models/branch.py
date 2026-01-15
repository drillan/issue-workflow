"""Git branch models."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from issue_workflow.models.issue import Issue


class BranchType(str, Enum):
    """Branch type prefixes."""

    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"


@dataclass(frozen=True)
class Branch:
    """Git branch information."""

    type: BranchType
    issue_number: int
    description: str

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if self.issue_number <= 0:
            raise ValueError(f"issue_number must be positive, got {self.issue_number}")

    @property
    def name(self) -> str:
        """Generate branch name."""
        return f"{self.type.value}/{self.issue_number}-{self.description}"

    @classmethod
    def from_issue(cls, issue: Issue, branch_type: BranchType) -> Branch:
        """Create branch from Issue."""
        description = cls._normalize_description(issue.title)
        return cls(type=branch_type, issue_number=issue.number, description=description)

    @staticmethod
    def _normalize_description(title: str, max_length: int = 40) -> str:
        """Normalize title for branch name.

        - Lowercase
        - Remove special characters
        - Replace spaces with hyphens
        - Limit to max_length characters
        """
        # Convert to lowercase
        normalized = title.lower()
        # Remove special characters (keep alphanumeric, spaces, and hyphens)
        normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
        # Replace spaces with hyphens
        normalized = re.sub(r"\s+", "-", normalized)
        # Remove consecutive hyphens
        normalized = re.sub(r"-+", "-", normalized)
        # Strip leading/trailing hyphens
        normalized = normalized.strip("-")
        # Limit length
        if len(normalized) > max_length:
            # Cut at word boundary if possible
            if "-" in normalized[:max_length]:
                normalized = normalized[: normalized.rfind("-", 0, max_length)]
            else:
                normalized = normalized[:max_length]
        return normalized

    @classmethod
    def extract_issue_number(cls, branch_name: str) -> int | None:
        """Extract issue number from branch name.

        Supports patterns like:
        - feat/123-xxx
        - fix/456-xxx
        - chore/123-xxx
        - docs/123-xxx
        - refactor/123-xxx
        - test/123-xxx
        - bugfix/123-xxx
        - feature/789-xxx (legacy)
        """
        pattern = r"^(?:feat|fix|chore|docs|refactor|test|feature|bugfix)/(\d+)-"
        match = re.match(pattern, branch_name)
        if match:
            return int(match.group(1))
        return None
