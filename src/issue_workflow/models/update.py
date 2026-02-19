"""Data models for update command."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FileChangeType(str, Enum):
    """Type of file change."""

    ADDED = "added"
    UPDATED = "updated"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class FileChangeInfo:
    """Information about a file change.

    Attributes:
        path: Relative path (e.g., .claude/skills/start-issue/SKILL.md)
        change_type: Type of change
        source_path: Source path for update (None for deleted files)
    """

    path: Path
    change_type: FileChangeType
    source_path: Path | None = None

    def __post_init__(self) -> None:
        """Validate invariants after initialization."""
        if (
            self.change_type in (FileChangeType.ADDED, FileChangeType.UPDATED)
            and self.source_path is None
        ):
            msg = f"{self.change_type.value} requires source_path"
            raise ValueError(msg)


@dataclass
class UpdateResult:
    """Result of update operation.

    Attributes:
        skills_changes: List of changes to skill directories
        agents_changes: List of changes to agent files
        errors: List of (path, error_message) tuples
        dry_run: Whether this was a dry-run operation
    """

    skills_changes: list[FileChangeInfo] = field(default_factory=list)
    agents_changes: list[FileChangeInfo] = field(default_factory=list)
    errors: list[tuple[Path, str]] = field(default_factory=list)
    dry_run: bool = False

    def _count_by_type(self, change_type: FileChangeType) -> int:
        """Count changes matching the given type.

        Args:
            change_type: FileChangeType to count.

        Returns:
            Number of matching changes across skills and agents.
        """
        return sum(
            1 for c in self.skills_changes + self.agents_changes if c.change_type == change_type
        )

    @property
    def added_count(self) -> int:
        """Count of added files/directories."""
        return self._count_by_type(FileChangeType.ADDED)

    @property
    def updated_count(self) -> int:
        """Count of updated files/directories."""
        return self._count_by_type(FileChangeType.UPDATED)

    @property
    def has_changes(self) -> bool:
        """Whether there are any changes (added or updated)."""
        return self.added_count > 0 or self.updated_count > 0

    @property
    def has_errors(self) -> bool:
        """Whether there are any errors."""
        return len(self.errors) > 0

    @property
    def success(self) -> bool:
        """Whether the update was successful (no errors)."""
        return not self.has_errors
