"""Language preset models."""

from enum import Enum

from pydantic import BaseModel, Field

from issue_workflow.models.config import QualityCommands


class LanguageName(str, Enum):
    """Supported language presets."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    GENERIC = "generic"


class FileTemplate(BaseModel):
    """Template file definition."""

    path: str = Field(description="Target path (relative to .claude/)")
    template: str = Field(description="Template file name")


class LanguagePreset(BaseModel):
    """Language preset definition."""

    name: LanguageName = Field(description="Preset identifier")
    display_name: str = Field(description="Display name for UI")
    quality: QualityCommands = Field(description="Default quality commands")
    files: list[FileTemplate] = Field(description="Files to generate")
