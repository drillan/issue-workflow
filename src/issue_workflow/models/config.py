"""Workflow configuration models."""

from pydantic import BaseModel, Field


class QualityCommands(BaseModel):
    """Quality check command configuration."""

    lint: str = Field(description="Linter command")
    format: str = Field(description="Formatter command")
    typecheck: str = Field(description="Type checker command")
    test: str = Field(description="Test command")
    all: str = Field(description="All checks command")


class WorkflowSettings(BaseModel):
    """Workflow behavior settings."""

    tdd_required: bool = Field(default=True, description="Enforce TDD workflow")
    quality_gate_required: bool = Field(default=True, description="Enforce quality gate")
    auto_report: bool = Field(default=True, description="Enable automatic progress reporting")


class WorkflowConfig(BaseModel):
    """Project workflow configuration."""

    version: str = Field(default="1.0", description="Configuration file version")
    language: str = Field(description="Language preset name")
    quality: QualityCommands = Field(description="Quality check commands")
    workflow: WorkflowSettings = Field(
        default_factory=WorkflowSettings, description="Workflow settings"
    )

    model_config = {
        "json_schema_extra": {
            "$schema": "https://raw.githubusercontent.com/drillan/issue-workflow/main/schemas/workflow-config.schema.json"
        }
    }
