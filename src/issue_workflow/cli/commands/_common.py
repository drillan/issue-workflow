"""Shared helpers for CLI command modules."""

import json
from datetime import datetime
from pathlib import Path

from issue_workflow.cli import ui
from issue_workflow.models.claude_result import ClaudeResult
from issue_workflow.models.execution_log import ExecutionLog
from issue_workflow.services.execution_logger import LOG_BASE_DIR_NAME, ExecutionLogger

EXIT_SUCCESS: int = 0

TRUNCATE_LENGTH: int = 80


def build_log_result(raw_json: str, exit_code: int, timeout: int) -> dict[str, object]:
    """Build the result dict for ExecutionLog.

    Args:
        raw_json: Raw JSON output from claude -p.
        exit_code: Process exit code.
        timeout: Timeout value in seconds.

    Returns:
        Parsed JSON dict or error info dict.
    """
    if exit_code == -1:
        return {"error": "timeout", "timeout_seconds": timeout}
    try:
        parsed: dict[str, object] = json.loads(raw_json)
        return parsed
    except (json.JSONDecodeError, TypeError):
        return {"error": "parse_error", "raw": raw_json}


def log_execution(
    command_name: str,
    args: dict[str, str | int | bool],
    result: ClaudeResult,
    timeout: int,
) -> None:
    """Log a command execution to JSONL.

    Builds an ExecutionLog entry from the ClaudeResult and writes it
    to the log file. Prints a warning if the log write fails.

    Args:
        command_name: Subcommand name (e.g., "start-issue").
        args: Subcommand arguments dict.
        result: ClaudeResult from claude -p execution.
        timeout: Timeout value in seconds (for error context).
    """
    log_result = build_log_result(result.raw_json, result.exit_code, timeout)
    entry = ExecutionLog(
        timestamp=datetime.now().astimezone(),
        command=command_name,
        args=args,
        exit_code=result.exit_code,
        result=log_result,
    )
    try:
        logger = ExecutionLogger(base_dir=Path.cwd() / LOG_BASE_DIR_NAME)
        logger.log(entry)
    except OSError:
        ui.console.print(f"\\[{command_name}] Warning: Failed to write log file.")


def on_tool_use(name: str, input_str: str) -> None:
    """Print tool use event in verbose mode."""
    truncated = (
        input_str[:TRUNCATE_LENGTH] + "..." if len(input_str) > TRUNCATE_LENGTH else input_str
    )
    ui.console.print(f"\u25cf {name}({truncated})")
