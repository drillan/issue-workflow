"""Unit tests for shared command helpers."""

from unittest.mock import patch

from issue_workflow.cli.commands._common import build_log_result, on_tool_use


class TestBuildLogResult:
    """Tests for build_log_result helper."""

    def test_timeout_returns_error_dict(self) -> None:
        """exit_code=-1 returns timeout error dict."""
        result = build_log_result(raw_json="{}", exit_code=-1, timeout=600)

        assert result == {"error": "timeout", "timeout_seconds": 600}

    def test_valid_json_returns_parsed_dict(self) -> None:
        """Valid JSON string returns parsed dict."""
        raw = '{"type": "result", "subtype": "success"}'
        result = build_log_result(raw_json=raw, exit_code=0, timeout=3600)

        assert result == {"type": "result", "subtype": "success"}

    def test_invalid_json_returns_parse_error_dict(self) -> None:
        """Invalid JSON returns parse_error dict with raw content."""
        raw = "Error: not json"
        result = build_log_result(raw_json=raw, exit_code=1, timeout=3600)

        assert result == {"error": "parse_error", "raw": "Error: not json"}

    def test_empty_string_returns_parse_error_dict(self) -> None:
        """Empty string returns parse_error dict."""
        result = build_log_result(raw_json="", exit_code=1, timeout=3600)

        assert result == {"error": "parse_error", "raw": ""}

    def test_none_raw_json_returns_parse_error_dict(self) -> None:
        """TypeError from json.loads(None) returns parse_error dict."""
        # This tests the TypeError catch branch
        result = build_log_result(raw_json=None, exit_code=1, timeout=3600)  # type: ignore[arg-type]

        assert result["error"] == "parse_error"


class TestOnToolUse:
    """Tests for on_tool_use helper."""

    def test_short_input_not_truncated(self) -> None:
        """Input <= 80 chars is displayed as-is."""
        with patch("issue_workflow.cli.commands._common.ui") as mock_ui:
            on_tool_use("Bash", "ls -la")

            call_str = str(mock_ui.console.print.call_args)
            assert "Bash(ls -la)" in call_str
            assert "..." not in call_str

    def test_long_input_truncated_at_80(self) -> None:
        """Input > 80 chars is truncated with '...'."""
        long_input = "x" * 100

        with patch("issue_workflow.cli.commands._common.ui") as mock_ui:
            on_tool_use("Read", long_input)

            call_str = str(mock_ui.console.print.call_args)
            assert "..." in call_str
            # Should contain first 80 chars
            assert "x" * 80 in call_str

    def test_exactly_80_chars_not_truncated(self) -> None:
        """Input of exactly 80 chars is not truncated."""
        input_80 = "a" * 80

        with patch("issue_workflow.cli.commands._common.ui") as mock_ui:
            on_tool_use("Glob", input_80)

            call_str = str(mock_ui.console.print.call_args)
            assert "..." not in call_str
