"""In-memory workflow context for run command orchestration."""

from dataclasses import dataclass, field
from pathlib import Path

from issue_workflow.models.claude_result import ClaudeResult


@dataclass
class WorkflowContext:
    """In-memory context for run command step orchestration.

    Accumulates metadata across steps. Not persisted.
    Recovery from failures uses individual subcommands.
    """

    issue_number: int
    pr_number: int | None = None
    worktree_path: Path | None = None
    step_results: list[ClaudeResult] = field(default_factory=list)

    @property
    def has_error(self) -> bool:
        """Check if any step has failed."""
        return any(r.is_error or r.exit_code != 0 for r in self.step_results)

    @property
    def last_result(self) -> ClaudeResult | None:
        """Get the most recent step result."""
        return self.step_results[-1] if self.step_results else None

    @property
    def total_cost_usd(self) -> float:
        """Aggregate API cost across all steps."""
        return sum(r.total_cost_usd for r in self.step_results)

    @property
    def cwd_for_skill(self) -> Path | None:
        """Working directory for skill execution (worktree or None for current)."""
        return self.worktree_path

    def log_number_for_step(self, command: str) -> int | None:
        """Get the appropriate number for log file naming.

        Returns issue_number for start-issue, pr_number for PR-related commands.
        """
        if command == "start-issue":
            return self.issue_number
        if command in ("review-pr", "respond-comments", "merge-pr"):
            return self.pr_number
        return None
