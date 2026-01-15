"""Unit tests for WorkflowConfig model validation."""

import pytest
from pydantic import ValidationError

from issue_workflow.models.config import QualityCommands, WorkflowConfig, WorkflowSettings


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


class TestWorkflowConfig:
    """Tests for WorkflowConfig model."""

    def test_valid_config(self, sample_workflow_config: dict[str, object]) -> None:
        """Test creating valid workflow config."""
        config = WorkflowConfig(**sample_workflow_config)
        assert config.version == "1.0"
        assert config.language == "python"
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
