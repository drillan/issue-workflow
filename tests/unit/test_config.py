"""Unit tests for WorkflowConfig model validation."""

import pytest
from pydantic import ValidationError

from issue_workflow.models.config import (
    DDDSettings,
    DocumentationSettings,
    LanguageName,
    QualityCommands,
    WorkflowConfig,
    WorkflowSettings,
)


class TestQualityCommands:
    """Tests for QualityCommands model."""

    def test_valid_quality_commands(self) -> None:
        """Test creating valid quality commands."""
        commands = QualityCommands(
            lint="uv run ruff check --fix .",
            format="uv run ruff format .",
            typecheck="uv run mypy .",
            test="uv run pytest",
            all="uv run ruff check --fix . && uv run ruff format . && uv run mypy .",
        )
        assert commands.lint == "uv run ruff check --fix ."
        assert commands.format == "uv run ruff format ."
        assert commands.typecheck == "uv run mypy ."
        assert commands.test == "uv run pytest"
        assert "ruff" in commands.all

    def test_missing_required_field(self) -> None:
        """Test validation error when required field is missing."""
        with pytest.raises(ValidationError):
            QualityCommands(
                lint="uv run ruff check --fix .",
                format="uv run ruff format .",
                typecheck=None,
                test=None,
                all=None,
            )


class TestWorkflowSettings:
    """Tests for WorkflowSettings model."""

    def test_default_values(self) -> None:
        """Test default values are applied."""
        settings = WorkflowSettings()
        assert settings.tdd_required is True
        assert settings.quality_gate_required is True
        assert settings.auto_report is True

    def test_custom_values(self) -> None:
        """Test custom values override defaults."""
        settings = WorkflowSettings(
            tdd_required=False, quality_gate_required=False, auto_report=False
        )
        assert settings.tdd_required is False
        assert settings.quality_gate_required is False
        assert settings.auto_report is False

    def test_default_ci_review_is_false(self) -> None:
        """Test ci_review defaults to False."""
        settings = WorkflowSettings()
        assert settings.ci_review is False

    def test_ci_review_can_be_enabled(self) -> None:
        """Test ci_review can be set to True."""
        settings = WorkflowSettings(ci_review=True)
        assert settings.ci_review is True


class TestLanguageName:
    """Tests for LanguageName enum."""

    def test_language_name_values(self) -> None:
        """Test LanguageName has expected values."""
        assert LanguageName.PYTHON.value == "python"
        assert LanguageName.TYPESCRIPT.value == "typescript"
        assert LanguageName.GO.value == "go"
        assert LanguageName.RUST.value == "rust"
        assert LanguageName.GENERIC.value == "generic"

    def test_language_name_from_string(self) -> None:
        """Test LanguageName can be created from string."""
        assert LanguageName("python") == LanguageName.PYTHON

    def test_language_name_invalid_value(self) -> None:
        """Test invalid language value raises error."""
        with pytest.raises(ValueError):
            LanguageName("invalid")


class TestWorkflowConfig:
    """Tests for WorkflowConfig model."""

    def test_valid_config(self, sample_workflow_config: dict[str, object]) -> None:
        """Test creating valid workflow config."""
        config = WorkflowConfig(**sample_workflow_config)
        assert config.version == "1.0"
        assert config.language == LanguageName.PYTHON
        assert config.quality.lint == "uv run ruff check --fix ."
        assert config.workflow.tdd_required is True

    def test_default_version(self) -> None:
        """Test default version is applied."""
        config = WorkflowConfig(
            language="python",
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
        )
        assert config.version == "1.0"

    def test_default_workflow_settings(self) -> None:
        """Test default workflow settings are applied."""
        config = WorkflowConfig(
            language="python",
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
        )
        assert config.workflow.tdd_required is True
        assert config.workflow.quality_gate_required is True

    def test_json_serialization(self, sample_workflow_config: dict[str, object]) -> None:
        """Test config can be serialized to JSON."""
        config = WorkflowConfig(**sample_workflow_config)
        json_str = config.model_dump_json()
        assert "python" in json_str
        assert "1.0" in json_str

    def test_missing_language(self) -> None:
        """Test validation error when language is missing."""
        with pytest.raises(ValidationError):
            WorkflowConfig(  # type: ignore[call-arg]
                quality=QualityCommands(
                    lint="lint",
                    format="format",
                    typecheck="typecheck",
                    test="test",
                    all="all",
                ),
            )

    def test_language_accepts_enum(self) -> None:
        """Test language field accepts LanguageName enum."""
        config = WorkflowConfig(
            language=LanguageName.PYTHON,
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
        )
        assert config.language == LanguageName.PYTHON

    def test_language_accepts_valid_string(self) -> None:
        """Test language field accepts valid string and converts to enum."""
        config = WorkflowConfig(
            language="python",
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
        )
        assert config.language == LanguageName.PYTHON

    def test_language_rejects_invalid(self) -> None:
        """Test language field rejects invalid values."""
        with pytest.raises(ValidationError):
            WorkflowConfig(
                language="invalid_language",
                quality=QualityCommands(
                    lint="lint",
                    format="format",
                    typecheck="typecheck",
                    test="test",
                    all="all",
                ),
            )

    def test_default_documentation_settings(self) -> None:
        """Test default documentation settings are applied."""
        config = WorkflowConfig(
            language="python",
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
        )
        assert config.documentation.paths == ["README.md", "docs/"]
        assert config.documentation.changelog == "CHANGELOG.md"
        assert config.documentation.ddd.enabled is True

    def test_custom_documentation_settings(self) -> None:
        """Test custom documentation settings are applied."""
        config = WorkflowConfig(
            language="python",
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
            documentation=DocumentationSettings(
                paths=["README.md", "specs/"],
                changelog="CHANGELOG.md",
                ddd=DDDSettings(enabled=False),
            ),
        )
        assert config.documentation.paths == ["README.md", "specs/"]
        assert config.documentation.ddd.enabled is False


class TestDDDSettings:
    """Tests for DDDSettings model."""

    def test_default_values(self) -> None:
        """Test default values are applied."""
        settings = DDDSettings()
        assert settings.enabled is True
        assert settings.retcon_writing is True

    def test_custom_values(self) -> None:
        """Test custom values override defaults."""
        settings = DDDSettings(enabled=False, retcon_writing=False)
        assert settings.enabled is False
        assert settings.retcon_writing is False

    def test_partial_custom_values(self) -> None:
        """Test partial custom values with defaults."""
        settings = DDDSettings(enabled=False)
        assert settings.enabled is False
        assert settings.retcon_writing is True


class TestDocumentationSettings:
    """Tests for DocumentationSettings model."""

    def test_default_values(self) -> None:
        """Test default values are applied."""
        settings = DocumentationSettings()
        assert settings.paths == ["README.md", "docs/"]
        assert settings.changelog == "CHANGELOG.md"
        assert settings.ddd.enabled is True
        assert settings.ddd.retcon_writing is True

    def test_custom_paths(self) -> None:
        """Test custom paths override defaults."""
        settings = DocumentationSettings(paths=["README.md", "specs/"])
        assert settings.paths == ["README.md", "specs/"]

    def test_empty_paths_allowed(self) -> None:
        """Test empty paths list is allowed."""
        settings = DocumentationSettings(paths=[])
        assert settings.paths == []

    def test_custom_changelog(self) -> None:
        """Test custom changelog path."""
        settings = DocumentationSettings(changelog="HISTORY.md")
        assert settings.changelog == "HISTORY.md"

    def test_changelog_none(self) -> None:
        """Test changelog can be None."""
        settings = DocumentationSettings(changelog=None)
        assert settings.changelog is None

    def test_ddd_disabled(self) -> None:
        """Test DDD can be disabled."""
        settings = DocumentationSettings(ddd=DDDSettings(enabled=False))
        assert settings.ddd.enabled is False
        assert settings.ddd.retcon_writing is True

    def test_full_custom_config(self) -> None:
        """Test fully customized documentation settings."""
        settings = DocumentationSettings(
            paths=["README.md", "api-docs/"],
            changelog="RELEASES.md",
            ddd=DDDSettings(enabled=True, retcon_writing=False),
        )
        assert settings.paths == ["README.md", "api-docs/"]
        assert settings.changelog == "RELEASES.md"
        assert settings.ddd.enabled is True
        assert settings.ddd.retcon_writing is False

    def test_empty_string_path_filtered(self) -> None:
        """Test empty string paths are filtered out."""
        settings = DocumentationSettings(paths=["README.md", "", "docs/"])
        assert settings.paths == ["README.md", "docs/"]

    def test_whitespace_only_path_filtered(self) -> None:
        """Test whitespace-only paths are filtered out."""
        settings = DocumentationSettings(paths=["README.md", "  ", "docs/"])
        assert settings.paths == ["README.md", "docs/"]

    def test_path_whitespace_stripped(self) -> None:
        """Test leading/trailing whitespace is stripped from paths."""
        settings = DocumentationSettings(paths=["  README.md  ", "  docs/  "])
        assert settings.paths == ["README.md", "docs/"]

    def test_changelog_empty_string_becomes_none(self) -> None:
        """Test empty string changelog becomes None."""
        settings = DocumentationSettings(changelog="")
        assert settings.changelog is None

    def test_changelog_whitespace_only_becomes_none(self) -> None:
        """Test whitespace-only changelog becomes None."""
        settings = DocumentationSettings(changelog="   ")
        assert settings.changelog is None

    def test_changelog_whitespace_stripped(self) -> None:
        """Test leading/trailing whitespace is stripped from changelog."""
        settings = DocumentationSettings(changelog="  HISTORY.md  ")
        assert settings.changelog == "HISTORY.md"
