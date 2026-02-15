"""Service for writing JSONL execution logs."""

from datetime import datetime
from pathlib import Path

from issue_workflow.models.execution_log import ExecutionLog

LOG_BASE_DIR_NAME: str = ".issue-workflow"
LOG_DIR_NAME: str = "logs"


class ExecutionLogger:
    """Service for writing JSONL execution logs."""

    def __init__(self, base_dir: Path) -> None:
        """Initialize with base log directory.

        Args:
            base_dir: Base directory for log files (e.g., project root).
        """
        self._base_dir = base_dir

    def log(self, entry: ExecutionLog) -> Path:
        """Write log entry and return log file path.

        Args:
            entry: ExecutionLog entry to write.

        Returns:
            Path to the log file.
        """
        number = self._extract_number(entry)
        log_path = self.get_log_path(entry.command, number=number)
        json_line = entry.model_dump_json()

        with log_path.open("a") as f:
            f.write(json_line + "\n")

        return log_path

    def get_log_path(
        self,
        command: str,
        number: int | None = None,
    ) -> Path:
        """Generate log file path.

        Format: base_dir/logs/YYYY-MM-DD/<command>-<number>-<ISO8601>.jsonl
        or: base_dir/logs/YYYY-MM-DD/<command>-<ISO8601>.jsonl (without number)

        Args:
            command: Subcommand name (e.g., "start-issue").
            number: Optional issue/PR number for the filename.

        Returns:
            Path to the log file.
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y-%m-%dT%H-%M-%S")

        log_dir = self._base_dir / LOG_DIR_NAME / date_str
        log_dir.mkdir(parents=True, exist_ok=True)

        if number is not None:
            filename = f"{command}-{number}-{time_str}.jsonl"
        else:
            filename = f"{command}-{time_str}.jsonl"

        return log_dir / filename

    def _extract_number(self, entry: ExecutionLog) -> int | None:
        """Extract issue/PR number from log entry args.

        Args:
            entry: ExecutionLog entry to extract number from.

        Returns:
            Number if found, None otherwise.
        """
        for key in ("issue_number", "pr_number"):
            value = entry.args.get(key)
            if isinstance(value, int):
                return value
        return None
