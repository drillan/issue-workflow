"""Service for executing claude -p as subprocess."""

import json
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from issue_workflow.models.claude_result import ClaudeResult

DEFAULT_TIMEOUT_SECONDS: int = 3600
_DISALLOWED_TOOLS: list[str] = ["AskUserQuestion"]


class ClaudeRunner:
    """Service for executing claude -p as subprocess."""

    def run(
        self,
        prompt: str,
        *,
        cwd: Path | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        verbose: bool = False,
        on_tool_use: Callable[[str, str], None] | None = None,
    ) -> ClaudeResult:
        """Execute claude -p and return the result.

        Args:
            prompt: Prompt text to send to claude.
            cwd: Working directory for subprocess execution.
            timeout_seconds: Timeout in seconds for the execution.
            verbose: If True, use stream-json format with real-time output.
            on_tool_use: Callback for tool_use events (verbose mode only).

        Returns:
            ClaudeResult with execution results.
        """
        if verbose:
            return self._run_verbose(
                prompt,
                cwd=cwd,
                timeout_seconds=timeout_seconds,
                on_tool_use=on_tool_use,
            )
        return self._run_non_verbose(prompt, cwd=cwd, timeout_seconds=timeout_seconds)

    def _build_base_cmd(self, prompt: str) -> list[str]:
        """Build base claude command with common flags.

        Args:
            prompt: Prompt text to send to claude.

        Returns:
            Base command list without output format flags.
        """
        cmd = [
            "claude",
            "-p",
            prompt,
            "--dangerously-skip-permissions",
        ]
        for tool in _DISALLOWED_TOOLS:
            cmd.extend(["--disallowed-tools", tool])
        return cmd

    def _run_non_verbose(
        self,
        prompt: str,
        *,
        cwd: Path | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> ClaudeResult:
        """Execute claude -p in non-verbose mode using subprocess.run."""
        cmd = self._build_base_cmd(prompt)
        cmd.extend(["--output-format", "json"])

        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return ClaudeResult(
                exit_code=-1,
                is_error=True,
                raw_json="{}",
            )

        raw_stdout = proc.stdout

        try:
            result = ClaudeResult.model_validate_json(raw_stdout)
        except (ValidationError, ValueError):
            return ClaudeResult(
                exit_code=proc.returncode,
                is_error=True,
                raw_json=raw_stdout,
            )

        return ClaudeResult(
            **result.model_dump(),
            exit_code=proc.returncode,
            raw_json=raw_stdout,
        )

    def _run_verbose(
        self,
        prompt: str,
        *,
        cwd: Path | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        on_tool_use: Callable[[str, str], None] | None = None,
    ) -> ClaudeResult:
        """Execute claude -p in verbose mode using subprocess.Popen."""
        cmd = self._build_base_cmd(prompt)
        cmd.extend(["--output-format", "stream-json", "--verbose"])

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        last_result_line: str = ""
        start_time = time.monotonic()

        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                event_type = event.get("type", "")

                if event_type == "assistant" and on_tool_use is not None:
                    message = event.get("message", {})
                    content_list = message.get("content", []) if isinstance(message, dict) else []
                    if isinstance(content_list, list):
                        for content_item in content_list:
                            if (
                                isinstance(content_item, dict)
                                and content_item.get("type") == "tool_use"
                            ):
                                tool_name = str(content_item.get("name", ""))
                                tool_input = str(content_item.get("input", ""))
                                on_tool_use(tool_name, tool_input)

                if event_type == "result":
                    last_result_line = line

            elapsed = time.monotonic() - start_time
            remaining = max(0, timeout_seconds - elapsed)
            proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            return ClaudeResult(
                exit_code=-1,
                is_error=True,
                raw_json="{}",
            )

        if last_result_line:
            try:
                result = ClaudeResult.model_validate_json(last_result_line)
                return ClaudeResult(
                    **result.model_dump(),
                    exit_code=proc.returncode,
                    raw_json=last_result_line,
                )
            except (ValidationError, ValueError):
                return ClaudeResult(
                    exit_code=proc.returncode,
                    is_error=True,
                    raw_json=last_result_line,
                )

        return ClaudeResult(
            exit_code=proc.returncode,
            is_error=proc.returncode != 0,
            raw_json=last_result_line or "{}",
        )
