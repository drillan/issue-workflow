"""Execution log entry model for JSONL output."""

from datetime import datetime

from pydantic import BaseModel


class ExecutionLog(BaseModel):
    """Single execution log entry for JSONL output."""

    timestamp: datetime
    command: str
    args: dict[str, str | int | bool]
    exit_code: int
    result: dict[str, object]
