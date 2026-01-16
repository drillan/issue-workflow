"""Workflow configuration models."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class LanguageName(str, Enum):
    """Supported language presets."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    GENERIC = "generic"


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
    ci_review: bool = Field(default=False, description="Use CI-based PR review instead of local")


class DDDSettings(BaseModel):
    """DDD (Documentation-Driven Development) settings."""

    enabled: bool = Field(default=True, description="Enable DDD workflow")
    retcon_writing: bool = Field(default=True, description="Enforce retcon writing style")


class DocumentationSettings(BaseModel):
    """Documentation configuration settings."""

    paths: list[str] = Field(
        default=["README.md", "docs/"],
        description="Documentation file/directory paths",
    )
    changelog: str | None = Field(
        default="CHANGELOG.md",
        description="Changelog file path",
    )
    ddd: DDDSettings = Field(
        default_factory=DDDSettings,
        description="DDD workflow settings",
    )

    @field_validator("paths", mode="before")
    @classmethod
    def validate_paths(cls, v: list[str]) -> list[str]:
        """Strip whitespace and filter out empty paths."""
        return [path.strip() for path in v if path.strip()]

    @field_validator("changelog", mode="before")
    @classmethod
    def validate_changelog(cls, v: str | None) -> str | None:
        """Strip whitespace and convert empty string to None."""
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class WorkflowConfig(BaseModel):
    """Project workflow configuration."""

    version: str = Field(default="1.0", description="Configuration file version")
    language: LanguageName = Field(description="Language preset name")
    quality: QualityCommands = Field(description="Quality check commands")
    workflow: WorkflowSettings = Field(
        default_factory=WorkflowSettings, description="Workflow settings"
    )
    documentation: DocumentationSettings = Field(
        default_factory=DocumentationSettings, description="Documentation settings"
    )

    model_config = {
        "json_schema_extra": {
            "$schema": "https://raw.githubusercontent.com/drillan/issue-workflow/main/schemas/workflow-config.schema.json"
        }
    }
