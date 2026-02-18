"""Unit tests for ClaudeResult model."""

import json

import pytest
from pydantic import ValidationError

from issue_workflow.models.claude_result import ClaudeResult


class TestClaudeResultCreation:
    """Tests for ClaudeResult model instantiation."""

    def test_default_values(self) -> None:
        """Test ClaudeResult creates with all default values."""
        result = ClaudeResult()
        assert result.type == "result"
        assert result.subtype == ""
        assert result.is_error is False
        assert result.result == ""
        assert result.duration_ms == 0
        assert result.duration_api_ms == 0
        assert result.num_turns == 0
        assert result.total_cost_usd == 0.0
        assert result.session_id == ""
        assert result.uuid == ""
        assert result.exit_code == 0
        assert result.raw_json == ""

    def test_custom_values(self) -> None:
        """Test ClaudeResult with custom field values."""
        result = ClaudeResult(
            type="result",
            subtype="success",
            is_error=False,
            result="hello world",
            duration_ms=1500,
            duration_api_ms=1200,
            num_turns=3,
            total_cost_usd=0.05,
            session_id="sess-123",
            uuid="uuid-456",
            exit_code=0,
            raw_json='{"type": "result"}',
        )
        assert result.subtype == "success"
        assert result.result == "hello world"
        assert result.duration_ms == 1500
        assert result.duration_api_ms == 1200
        assert result.num_turns == 3
        assert result.total_cost_usd == 0.05
        assert result.session_id == "sess-123"
        assert result.uuid == "uuid-456"

    def test_frozen_immutability(self) -> None:
        """Test ClaudeResult fields cannot be modified after creation."""
        result = ClaudeResult()
        with pytest.raises(ValidationError):
            result.result = "modified"  # type: ignore[misc]


class TestClaudeResultExcludedFields:
    """Tests for exit_code and raw_json excluded from serialization."""

    def test_exit_code_excluded_from_model_dump(self) -> None:
        """Test exit_code is not included in model_dump output."""
        result = ClaudeResult(exit_code=1)
        dumped = result.model_dump()
        assert "exit_code" not in dumped

    def test_raw_json_excluded_from_model_dump(self) -> None:
        """Test raw_json is not included in model_dump output."""
        result = ClaudeResult(raw_json='{"foo": "bar"}')
        dumped = result.model_dump()
        assert "raw_json" not in dumped

    def test_exit_code_excluded_from_json(self) -> None:
        """Test exit_code is not included in model_dump_json output."""
        result = ClaudeResult(exit_code=1)
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        assert "exit_code" not in parsed

    def test_raw_json_excluded_from_json(self) -> None:
        """Test raw_json is not included in model_dump_json output."""
        result = ClaudeResult(raw_json='{"foo": "bar"}')
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        assert "raw_json" not in parsed

    def test_exit_code_accessible_as_attribute(self) -> None:
        """Test exit_code is still accessible on the model instance."""
        result = ClaudeResult(exit_code=42)
        assert result.exit_code == 42

    def test_raw_json_accessible_as_attribute(self) -> None:
        """Test raw_json is still accessible on the model instance."""
        result = ClaudeResult(raw_json='{"test": true}')
        assert result.raw_json == '{"test": true}'


class TestClaudeResultParsing:
    """Tests for model_validate_json parsing."""

    def test_model_validate_json_success(self) -> None:
        """Test parsing valid JSON output from claude -p."""
        raw = json.dumps(
            {
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "result": "hello",
                "duration_ms": 1393,
                "duration_api_ms": 1281,
                "num_turns": 1,
                "total_cost_usd": 0.04386575,
                "session_id": "0baf1b02-test",
                "uuid": "45b9e716-test",
            }
        )
        result = ClaudeResult.model_validate_json(raw)
        assert result.type == "result"
        assert result.subtype == "success"
        assert result.result == "hello"
        assert result.duration_ms == 1393
        assert result.total_cost_usd == pytest.approx(0.04386575)

    def test_model_validate_json_partial_fields(self) -> None:
        """Test parsing JSON with only some fields present."""
        raw = json.dumps({"type": "result", "subtype": "success"})
        result = ClaudeResult.model_validate_json(raw)
        assert result.type == "result"
        assert result.subtype == "success"
        assert result.result == ""
        assert result.duration_ms == 0

    def test_model_validate_json_ignores_extra_fields(self) -> None:
        """Test parsing JSON with extra fields not in the model."""
        raw = json.dumps(
            {
                "type": "result",
                "subtype": "success",
                "stop_reason": None,
                "usage": {"input_tokens": 100},
                "errors": [],
            }
        )
        result = ClaudeResult.model_validate_json(raw)
        assert result.type == "result"
        assert result.subtype == "success"


class TestClaudeResultTimeoutConstruction:
    """Tests for timeout scenario construction."""

    def test_timeout_construction(self) -> None:
        """Test constructing ClaudeResult for timeout case."""
        result = ClaudeResult(
            exit_code=-1,
            is_error=True,
            raw_json="{}",
        )
        assert result.exit_code == -1
        assert result.is_error is True
        assert result.raw_json == "{}"
        assert result.result == ""
        assert result.type == "result"
