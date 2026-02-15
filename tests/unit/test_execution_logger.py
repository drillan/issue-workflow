"""Unit tests for ExecutionLogger service."""

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from issue_workflow.models.execution_log import ExecutionLog
from issue_workflow.services.execution_logger import (
    LOG_BASE_DIR_NAME,
    LOG_DIR_NAME,
    ExecutionLogger,
)


class TestExecutionLoggerGetLogPath:
    """Tests for ExecutionLogger.get_log_path method."""

    def test_path_with_number(self, tmp_path: Path) -> None:
        """Test log path format with issue/PR number."""
        logger = ExecutionLogger(base_dir=tmp_path)
        fixed_now = datetime(2026, 2, 15, 10, 30, 0)
        with patch("issue_workflow.services.execution_logger.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            path = logger.get_log_path("start-issue", number=199)

        assert path.name == "start-issue-199-2026-02-15T10-30-00.jsonl"

    def test_path_without_number(self, tmp_path: Path) -> None:
        """Test log path format without number."""
        logger = ExecutionLogger(base_dir=tmp_path)
        fixed_now = datetime(2026, 2, 15, 10, 45, 0)
        with patch("issue_workflow.services.execution_logger.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            path = logger.get_log_path("create-pr")

        assert path.name == "create-pr-2026-02-15T10-45-00.jsonl"

    def test_date_directory_created(self, tmp_path: Path) -> None:
        """Test date directory (YYYY-MM-DD) is created."""
        logger = ExecutionLogger(base_dir=tmp_path)
        fixed_now = datetime(2026, 2, 15, 10, 30, 0)
        with patch("issue_workflow.services.execution_logger.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            path = logger.get_log_path("start-issue", number=199)

        date_dir = path.parent
        assert date_dir.name == "2026-02-15"
        assert date_dir.exists()

    def test_path_under_base_dir(self, tmp_path: Path) -> None:
        """Test path is under base_dir/logs/YYYY-MM-DD/."""
        logger = ExecutionLogger(base_dir=tmp_path)
        fixed_now = datetime(2026, 2, 15, 10, 30, 0)
        with patch("issue_workflow.services.execution_logger.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            path = logger.get_log_path("start-issue", number=199)

        # Path should be: base_dir/logs/2026-02-15/start-issue-199-...
        assert path.parent.parent.name == "logs"
        assert str(path).startswith(str(tmp_path))


class TestExecutionLoggerLog:
    """Tests for ExecutionLogger.log method."""

    def test_writes_jsonl_line(self, tmp_path: Path) -> None:
        """Test log entry is written as single JSON line."""
        logger = ExecutionLogger(base_dir=tmp_path)
        entry = ExecutionLog(
            timestamp=datetime(2026, 2, 15, 10, 30, 0, tzinfo=UTC),
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result={"type": "result"},
        )
        log_path = logger.log(entry)

        content = log_path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["command"] == "start-issue"

    def test_returns_log_file_path(self, tmp_path: Path) -> None:
        """Test log method returns the path of the log file."""
        logger = ExecutionLogger(base_dir=tmp_path)
        entry = ExecutionLog(
            timestamp=datetime(2026, 2, 15, 10, 30, 0, tzinfo=UTC),
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result={"type": "result"},
        )
        log_path = logger.log(entry)

        assert log_path.exists()
        assert log_path.suffix == ".jsonl"

    def test_appends_to_existing_file(self, tmp_path: Path) -> None:
        """Test multiple log calls append to same file."""
        logger = ExecutionLogger(base_dir=tmp_path)
        entry1 = ExecutionLog(
            timestamp=datetime(2026, 2, 15, 10, 30, 0, tzinfo=UTC),
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result={"type": "result", "subtype": "success"},
        )
        entry2 = ExecutionLog(
            timestamp=datetime(2026, 2, 15, 10, 31, 0, tzinfo=UTC),
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result={"type": "result", "subtype": "success"},
        )
        path1 = logger.log(entry1)
        path2 = logger.log(entry2)

        assert path1 == path2
        content = path1.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 2


class TestExecutionLoggerConstants:
    """Tests for ExecutionLogger constants."""

    def test_log_base_dir_name(self) -> None:
        """Test LOG_BASE_DIR_NAME is '.issue-workflow'."""
        assert LOG_BASE_DIR_NAME == ".issue-workflow"

    def test_log_dir_name(self) -> None:
        """Test LOG_DIR_NAME is 'logs'."""
        assert LOG_DIR_NAME == "logs"
