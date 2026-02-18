"""Claude CLI execution result model."""

from pydantic import BaseModel, Field


class ClaudeResult(BaseModel, frozen=True):
    """Result from claude -p execution.

    claude -p --output-format json の JSON 出力をパースして構築する。
    model_validate_json(raw_stdout) で安全にパース可能。
    """

    type: str = "result"
    subtype: str = ""
    is_error: bool = False
    result: str = ""
    duration_ms: int = 0
    duration_api_ms: int = 0
    num_turns: int = 0
    total_cost_usd: float = 0.0
    session_id: str = ""
    uuid: str = ""
    exit_code: int = Field(default=0, exclude=True)
    raw_json: str = Field(default="", exclude=True)
