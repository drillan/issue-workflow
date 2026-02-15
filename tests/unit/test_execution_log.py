"""Unit tests for ExecutionLog model."""

import json
from datetime import UTC, datetime

from issue_workflow.models.execution_log import ExecutionLog


class TestExecutionLogCreation:
    """Tests for ExecutionLog model instantiation."""

    def test_valid_execution_log(self) -> None:
        """Test creating valid ExecutionLog with all fields."""
        now = datetime.now(tz=UTC)
        log = ExecutionLog(
            timestamp=now,
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result={"type": "result", "subtype": "success"},
        )
        assert log.timestamp == now
        assert log.command == "start-issue"
        assert log.args == {"issue_number": 199}
        assert log.exit_code == 0
        assert log.result == {"type": "result", "subtype": "success"}

    def test_command_stores_subcommand_name(self) -> None:
        """Test command stores only the subcommand name."""
        log = ExecutionLog(
            timestamp=datetime.now(tz=UTC),
            command="create-pr",
            args={},
            exit_code=0,
            result={},
        )
        assert log.command == "create-pr"

    def test_args_with_mixed_types(self) -> None:
        """Test args dict supports str, int, and bool values."""
        args: dict[str, str | int | bool] = {
            "issue_number": 199,
            "worktree": True,
            "branch": "feat/199-test",
        }
        log = ExecutionLog(
            timestamp=datetime.now(tz=UTC),
            command="start-issue",
            args=args,
            exit_code=0,
            result={},
        )
        assert log.args["issue_number"] == 199
        assert log.args["worktree"] is True
        assert log.args["branch"] == "feat/199-test"

    def test_result_stores_parsed_dict(self) -> None:
        """Test result field stores parsed JSON dict."""
        result_data: dict[str, object] = {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "duration_ms": 1500,
        }
        log = ExecutionLog(
            timestamp=datetime.now(tz=UTC),
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result=result_data,
        )
        assert log.result["type"] == "result"
        assert log.result["duration_ms"] == 1500


class TestExecutionLogSerialization:
    """Tests for ExecutionLog JSON serialization."""

    def test_model_dump_json(self) -> None:
        """Test serialization to JSON string."""
        now = datetime(2026, 2, 15, 10, 30, 0, tzinfo=UTC)
        log = ExecutionLog(
            timestamp=now,
            command="start-issue",
            args={"issue_number": 199},
            exit_code=0,
            result={"type": "result"},
        )
        json_str = log.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["command"] == "start-issue"
        assert parsed["exit_code"] == 0

    def test_model_dump_json_contains_all_fields(self) -> None:
        """Test all fields present in JSON output."""
        log = ExecutionLog(
            timestamp=datetime.now(tz=UTC),
            command="review-pr",
            args={"pr_number": 42},
            exit_code=1,
            result={"error": "timeout"},
        )
        json_str = log.model_dump_json()
        parsed = json.loads(json_str)
        assert "timestamp" in parsed
        assert "command" in parsed
        assert "args" in parsed
        assert "exit_code" in parsed
        assert "result" in parsed

    def test_timestamp_serialized_as_iso8601(self) -> None:
        """Test timestamp is serialized in ISO 8601 format."""
        now = datetime(2026, 2, 15, 10, 30, 0, tzinfo=UTC)
        log = ExecutionLog(
            timestamp=now,
            command="start-issue",
            args={},
            exit_code=0,
            result={},
        )
        json_str = log.model_dump_json()
        parsed = json.loads(json_str)
        # ISO 8601 format should be parseable
        parsed_ts = datetime.fromisoformat(parsed["timestamp"])
        assert parsed_ts == now
