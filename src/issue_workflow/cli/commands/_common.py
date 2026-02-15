"""Shared helpers for CLI command modules."""

import json

from issue_workflow.cli import ui

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


def on_tool_use(name: str, input_str: str) -> None:
    """Print tool use event in verbose mode."""
    truncated = (
        input_str[:TRUNCATE_LENGTH] + "..." if len(input_str) > TRUNCATE_LENGTH else input_str
    )
    ui.console.print(f"\u25cf {name}({truncated})")
