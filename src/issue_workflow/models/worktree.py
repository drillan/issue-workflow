"""Git worktree model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from issue_workflow.models.branch import Branch


@dataclass(frozen=True)
class Worktree:
    """Git worktree information."""

    path: Path
    branch: Branch
    project_name: str

    @property
    def directory_name(self) -> str:
        """Generate worktree directory name.

        Format: {project_name}-{branch_type}-{issue_number}-{description}
        Example: project-name-feat-123-add-feature
        """
        branch_part = self.branch.name.replace("/", "-")
        return f"{self.project_name}-{branch_part}"

    @property
    def full_path(self) -> Path:
        """Get full path to worktree directory.

        Worktrees are created in the parent directory of the main repository.
        """
        return self.path.parent / self.directory_name

    @classmethod
    def from_branch(cls, repo_path: Path, branch: Branch, project_name: str) -> Worktree:
        """Create Worktree from Branch."""
        return cls(path=repo_path, branch=branch, project_name=project_name)
