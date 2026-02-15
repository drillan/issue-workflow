"""Unit tests for ClaudeRunner service."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner


class TestClaudeRunnerNonVerbose:
    """Tests for ClaudeRunner.run in non-verbose mode."""

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_successful_execution(self, mock_run: MagicMock) -> None:
        """Test successful claude -p execution returns ClaudeResult."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "result": "hello",
                "duration_ms": 1000,
                "duration_api_ms": 900,
                "num_turns": 1,
                "total_cost_usd": 0.05,
                "session_id": "sess-123",
                "uuid": "uuid-456",
            }
        )
        mock_run.return_value = mock_result

        runner = ClaudeRunner()
        result = runner.run("test prompt")

        assert result.subtype == "success"
        assert result.result == "hello"
        assert result.exit_code == 0

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_passes_correct_args(self, mock_run: MagicMock) -> None:
        """Test claude is called with correct arguments."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"type": "result"})
        mock_run.return_value = mock_result

        runner = ClaudeRunner()
        runner.run("test prompt")

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "test prompt" in cmd
        assert "--dangerously-skip-permissions" in cmd
        assert "--output-format" in cmd
        assert "json" in cmd

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_with_custom_cwd(self, mock_run: MagicMock) -> None:
        """Test cwd parameter is passed to subprocess."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"type": "result"})
        mock_run.return_value = mock_result

        runner = ClaudeRunner()
        custom_path = Path("/tmp/test-dir")
        runner.run("prompt", cwd=custom_path)

        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("cwd") == custom_path

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_with_custom_timeout(self, mock_run: MagicMock) -> None:
        """Test timeout parameter is passed to subprocess."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"type": "result"})
        mock_run.return_value = mock_result

        runner = ClaudeRunner()
        runner.run("prompt", timeout_seconds=600)

        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs.get("timeout") == 600

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_timeout_returns_error_result(self, mock_run: MagicMock) -> None:
        """Test TimeoutExpired results in ClaudeResult with exit_code=-1."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=3600)

        runner = ClaudeRunner()
        result = runner.run("prompt")

        assert result.exit_code == -1
        assert result.is_error is True

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_nonzero_exit_code(self, mock_run: MagicMock) -> None:
        """Test non-zero exit code is captured in ClaudeResult."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps(
            {"type": "result", "subtype": "error_max_budget_usd", "is_error": True}
        )
        mock_run.return_value = mock_result

        runner = ClaudeRunner()
        result = runner.run("prompt")

        assert result.exit_code == 1
        assert result.is_error is True

    @patch("issue_workflow.services.claude_runner.subprocess.run")
    def test_run_stores_raw_json(self, mock_run: MagicMock) -> None:
        """Test raw stdout is stored in raw_json field."""
        raw_output = json.dumps({"type": "result", "subtype": "success"})
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = raw_output
        mock_run.return_value = mock_result

        runner = ClaudeRunner()
        result = runner.run("prompt")

        assert result.raw_json == raw_output


class TestClaudeRunnerVerbose:
    """Tests for ClaudeRunner.run in verbose mode."""

    @patch("issue_workflow.services.claude_runner.subprocess.Popen")
    def test_verbose_uses_popen(self, mock_popen: MagicMock) -> None:
        """Test verbose mode uses subprocess.Popen instead of run."""
        mock_process = MagicMock()
        mock_process.stdout = iter([json.dumps({"type": "result", "subtype": "success"}) + "\n"])
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        runner = ClaudeRunner()
        runner.run("prompt", verbose=True)

        mock_popen.assert_called_once()

    @patch("issue_workflow.services.claude_runner.subprocess.Popen")
    def test_verbose_passes_stream_json_format(self, mock_popen: MagicMock) -> None:
        """Test verbose uses --output-format stream-json --verbose."""
        mock_process = MagicMock()
        mock_process.stdout = iter([json.dumps({"type": "result", "subtype": "success"}) + "\n"])
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        runner = ClaudeRunner()
        runner.run("prompt", verbose=True)

        call_args = mock_popen.call_args[0][0]
        assert "--output-format" in call_args
        assert "stream-json" in call_args
        assert "--verbose" in call_args

    @patch("issue_workflow.services.claude_runner.subprocess.Popen")
    def test_verbose_on_tool_use_callback(self, mock_popen: MagicMock) -> None:
        """Test on_tool_use callback is called for tool_use events."""
        tool_use_event = json.dumps(
            {
                "type": "assistant",
                "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}],
            }
        )
        result_event = json.dumps({"type": "result", "subtype": "success"})

        mock_process = MagicMock()
        mock_process.stdout = iter([tool_use_event + "\n", result_event + "\n"])
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        callback = MagicMock()
        runner = ClaudeRunner()
        runner.run("prompt", verbose=True, on_tool_use=callback)

        callback.assert_called()

    @patch("issue_workflow.services.claude_runner.subprocess.Popen")
    def test_verbose_timeout(self, mock_popen: MagicMock) -> None:
        """Test verbose mode handles timeout."""
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.side_effect = [
            subprocess.TimeoutExpired(cmd="claude", timeout=3600),
            0,  # Second call after kill
        ]
        mock_process.kill.return_value = None
        mock_popen.return_value = mock_process

        runner = ClaudeRunner()
        result = runner.run("prompt", verbose=True)

        assert result.exit_code == -1
        assert result.is_error is True


class TestClaudeRunnerConstants:
    """Tests for ClaudeRunner constants."""

    def test_default_timeout_seconds(self) -> None:
        """Test DEFAULT_TIMEOUT_SECONDS is 3600."""
        assert DEFAULT_TIMEOUT_SECONDS == 3600
