"""Language preset models."""

from pydantic import BaseModel, Field

from issue_workflow.models.config import (
    DocumentationSettings,
    LanguageName,
    QualityCommands,
)

__all__ = ["FileTemplate", "LanguageName", "LanguagePreset"]


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
    documentation: DocumentationSettings = Field(
        default_factory=DocumentationSettings,
        description="Documentation settings",
    )
