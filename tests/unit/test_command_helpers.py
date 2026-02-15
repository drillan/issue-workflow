"""Unit tests for shared command helpers."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from issue_workflow.cli.commands._common import build_log_result, on_tool_use
from tests.conftest import make_claude_result

_MOD = "issue_workflow.cli.commands._common"


class TestRunClaudeSkill:
    """Tests for run_claude_skill shared helper."""

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_returns_exit_code_from_claude_result(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Returns the exit_code from ClaudeResult."""
        mock_runner_cls.return_value.run.return_value = make_claude_result(exit_code=0)

        from issue_workflow.cli.commands._common import run_claude_skill

        exit_code = run_claude_skill("test-cmd", "/test-prompt", {}, verbose=False, timeout=3600)

        assert exit_code == 0

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_returns_nonzero_exit_code(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Returns nonzero exit_code when Claude fails."""
        mock_runner_cls.return_value.run.return_value = make_claude_result(
            exit_code=1, is_error=True
        )

        from issue_workflow.cli.commands._common import run_claude_skill

        exit_code = run_claude_skill("test-cmd", "/test-prompt", {}, verbose=False, timeout=3600)

        assert exit_code == 1

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_passes_prompt_to_runner(self, mock_runner_cls: MagicMock, mock_log: MagicMock) -> None:
        """Prompt is forwarded to ClaudeRunner.run."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/my-skill 123", {}, verbose=False, timeout=3600)

        call_args = mock_runner_cls.return_value.run.call_args
        assert call_args[0][0] == "/my-skill 123"

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_passes_cwd_to_runner(self, mock_runner_cls: MagicMock, mock_log: MagicMock) -> None:
        """cwd is forwarded to ClaudeRunner.run."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        test_path = Path("/tmp/test")
        run_claude_skill("test-cmd", "/test", {}, cwd=test_path, verbose=False, timeout=3600)

        call_kwargs = mock_runner_cls.return_value.run.call_args
        assert call_kwargs.kwargs.get("cwd") == test_path

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_cwd_defaults_to_none(self, mock_runner_cls: MagicMock, mock_log: MagicMock) -> None:
        """cwd defaults to None when not specified."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/test", {}, verbose=False, timeout=3600)

        call_kwargs = mock_runner_cls.return_value.run.call_args
        assert call_kwargs.kwargs.get("cwd") is None

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_passes_verbose_to_runner(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """verbose=True is forwarded to ClaudeRunner.run."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/test", {}, verbose=True, timeout=3600)

        call_kwargs = mock_runner_cls.return_value.run.call_args
        assert call_kwargs.kwargs.get("verbose") is True

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_passes_timeout_to_runner(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Custom timeout is forwarded to ClaudeRunner.run."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/test", {}, verbose=False, timeout=600)

        call_kwargs = mock_runner_cls.return_value.run.call_args
        assert call_kwargs.kwargs.get("timeout_seconds") == 600

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_verbose_passes_on_tool_use_callback(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Verbose mode passes on_tool_use callback."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/test", {}, verbose=True, timeout=3600)

        call_kwargs = mock_runner_cls.return_value.run.call_args
        assert call_kwargs.kwargs.get("on_tool_use") is not None

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_non_verbose_no_on_tool_use_callback(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Non-verbose mode does not pass on_tool_use callback."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/test", {}, verbose=False, timeout=3600)

        call_kwargs = mock_runner_cls.return_value.run.call_args
        assert call_kwargs.kwargs.get("on_tool_use") is None

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_calls_log_execution_with_correct_args(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """log_execution is called with command_name, log_args, result, timeout."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        from issue_workflow.cli.commands._common import run_claude_skill

        run_claude_skill("test-cmd", "/test", {"pr_number": 300}, verbose=False, timeout=600)

        mock_log.assert_called_once()
        assert mock_log.call_args[0][0] == "test-cmd"
        assert mock_log.call_args[0][1] == {"pr_number": 300}
        assert mock_log.call_args[0][3] == 600

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_starting_message_printed(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Console shows '[command] Starting...'."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands._common import run_claude_skill

            run_claude_skill("test-cmd", "/test", {}, verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[test-cmd] Starting" in c for c in all_calls)

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_done_message_printed(self, mock_runner_cls: MagicMock, mock_log: MagicMock) -> None:
        """Console shows '[command] Done. (exit_code=N)'."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands._common import run_claude_skill

            run_claude_skill("test-cmd", "/test", {}, verbose=False, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("[test-cmd] Done" in c and "exit_code=0" in c for c in all_calls)

    @patch(f"{_MOD}.log_execution")
    @patch(f"{_MOD}.ClaudeRunner")
    def test_verbose_starting_message(
        self, mock_runner_cls: MagicMock, mock_log: MagicMock
    ) -> None:
        """Verbose mode shows '(verbose mode)' in starting message."""
        mock_runner_cls.return_value.run.return_value = make_claude_result()

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands._common import run_claude_skill

            run_claude_skill("test-cmd", "/test", {}, verbose=True, timeout=3600)

            all_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("verbose mode" in c for c in all_calls)


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
        with patch(f"{_MOD}.ui") as mock_ui:
            on_tool_use("Bash", "ls -la")

            call_str = str(mock_ui.console.print.call_args)
            assert "Bash(ls -la)" in call_str
            assert "..." not in call_str

    def test_long_input_truncated_at_80(self) -> None:
        """Input > 80 chars is truncated with '...'."""
        long_input = "x" * 100

        with patch(f"{_MOD}.ui") as mock_ui:
            on_tool_use("Read", long_input)

            call_str = str(mock_ui.console.print.call_args)
            assert "..." in call_str
            # Should contain first 80 chars
            assert "x" * 80 in call_str

    def test_exactly_80_chars_not_truncated(self) -> None:
        """Input of exactly 80 chars is not truncated."""
        input_80 = "a" * 80

        with patch(f"{_MOD}.ui") as mock_ui:
            on_tool_use("Glob", input_80)

            call_str = str(mock_ui.console.print.call_args)
            assert "..." not in call_str


class TestLogExecution:
    """Tests for log_execution helper."""

    @patch(f"{_MOD}.ExecutionLogger")
    def test_creates_log_entry_with_correct_command(self, mock_logger_cls: MagicMock) -> None:
        """ExecutionLog.command matches command_name."""
        from issue_workflow.cli.commands._common import log_execution

        result = make_claude_result()
        log_execution("test-cmd", {"key": "value"}, result, 3600)

        entry = mock_logger_cls.return_value.log.call_args[0][0]
        assert entry.command == "test-cmd"

    @patch(f"{_MOD}.ExecutionLogger")
    def test_creates_log_entry_with_correct_args(self, mock_logger_cls: MagicMock) -> None:
        """ExecutionLog.args matches provided args."""
        from issue_workflow.cli.commands._common import log_execution

        result = make_claude_result()
        log_execution("test-cmd", {"pr_number": 300}, result, 3600)

        entry = mock_logger_cls.return_value.log.call_args[0][0]
        assert entry.args == {"pr_number": 300}

    @patch(f"{_MOD}.ExecutionLogger")
    def test_creates_log_entry_with_exit_code(self, mock_logger_cls: MagicMock) -> None:
        """ExecutionLog.exit_code matches ClaudeResult.exit_code."""
        from issue_workflow.cli.commands._common import log_execution

        result = make_claude_result(exit_code=1, is_error=True)
        log_execution("test-cmd", {}, result, 3600)

        entry = mock_logger_cls.return_value.log.call_args[0][0]
        assert entry.exit_code == 1

    @patch(f"{_MOD}.ExecutionLogger")
    def test_creates_log_entry_with_parsed_result(self, mock_logger_cls: MagicMock) -> None:
        """ExecutionLog.result is parsed from raw_json."""
        from issue_workflow.cli.commands._common import log_execution

        result = make_claude_result()
        log_execution("test-cmd", {}, result, 3600)

        entry = mock_logger_cls.return_value.log.call_args[0][0]
        assert entry.result["type"] == "result"
        assert entry.result["subtype"] == "success"

    @patch(f"{_MOD}.ExecutionLogger")
    def test_timeout_result(self, mock_logger_cls: MagicMock) -> None:
        """Timeout case: result contains error info."""
        from issue_workflow.cli.commands._common import log_execution

        result = make_claude_result(exit_code=-1, is_error=True, raw_json="{}")
        log_execution("test-cmd", {}, result, 3600)

        entry = mock_logger_cls.return_value.log.call_args[0][0]
        assert entry.exit_code == -1
        assert entry.result["error"] == "timeout"

    @patch(f"{_MOD}.ExecutionLogger")
    def test_os_error_prints_warning(self, mock_logger_cls: MagicMock) -> None:
        """OSError in logger prints warning."""
        mock_logger_cls.return_value.log.side_effect = OSError("Permission denied")

        with patch(f"{_MOD}.ui") as mock_ui:
            from issue_workflow.cli.commands._common import log_execution

            log_execution("test-cmd", {}, make_claude_result(), 3600)

            warning_calls = [str(c) for c in mock_ui.console.print.call_args_list]
            assert any("log" in c.lower() for c in warning_calls)

    @patch(f"{_MOD}.ExecutionLogger")
    def test_os_error_does_not_raise(self, mock_logger_cls: MagicMock) -> None:
        """OSError in logger does not propagate."""
        mock_logger_cls.return_value.log.side_effect = OSError("Permission denied")

        from issue_workflow.cli.commands._common import log_execution

        # Should not raise
        log_execution("test-cmd", {}, make_claude_result(), 3600)
