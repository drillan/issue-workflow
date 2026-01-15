"""Unit tests for TemplateService class."""

import json
from pathlib import Path

import pytest

from issue_workflow.models.config import LanguageName, QualityCommands
from issue_workflow.models.preset import LanguagePreset
from issue_workflow.services.template import TemplateService


@pytest.fixture
def python_preset() -> LanguagePreset:
    """Create a Python language preset for testing."""
    return LanguagePreset(
        name=LanguageName.PYTHON,
        display_name="Python",
        quality=QualityCommands(
            lint="ruff check .",
            format="ruff format .",
            typecheck="mypy .",
            test="pytest",
            all="ruff check . && ruff format . && mypy . && pytest",
        ),
        files=[],
    )


@pytest.fixture
def typescript_preset() -> LanguagePreset:
    """Create a TypeScript language preset for testing."""
    return LanguagePreset(
        name=LanguageName.TYPESCRIPT,
        display_name="TypeScript",
        quality=QualityCommands(
            lint="eslint .",
            format="prettier --write .",
            typecheck="tsc --noEmit",
            test="npm test",
            all="eslint . && prettier --write . && tsc --noEmit && npm test",
        ),
        files=[],
    )


class TestGenerateWorkflowConfig:
    """Tests for generate_workflow_config method."""

    def test_generates_config_file(self, tmp_path: Path, python_preset: LanguagePreset) -> None:
        """Test config file is created in target directory."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        result = service.generate_workflow_config(python_preset, target_dir)

        assert result.exists()
        assert result.name == "workflow-config.json"
        assert result.parent == target_dir

    def test_creates_target_directory(self, tmp_path: Path, python_preset: LanguagePreset) -> None:
        """Test target directory is created if not exists."""
        service = TemplateService()
        target_dir = tmp_path / "nested" / "path" / ".claude"

        service.generate_workflow_config(python_preset, target_dir)

        assert target_dir.exists()

    def test_config_contains_language(self, tmp_path: Path, python_preset: LanguagePreset) -> None:
        """Test generated config contains correct language."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        config_path = service.generate_workflow_config(python_preset, target_dir)

        with config_path.open() as f:
            config = json.load(f)
        assert config["language"] == "python"

    def test_config_contains_quality_commands(
        self, tmp_path: Path, python_preset: LanguagePreset
    ) -> None:
        """Test generated config contains quality commands from preset."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        config_path = service.generate_workflow_config(python_preset, target_dir)

        with config_path.open() as f:
            config = json.load(f)
        assert config["quality"]["lint"] == "ruff check ."
        assert config["quality"]["format"] == "ruff format ."
        assert config["quality"]["typecheck"] == "mypy ."
        assert config["quality"]["test"] == "pytest"

    def test_config_contains_version(self, tmp_path: Path, python_preset: LanguagePreset) -> None:
        """Test generated config contains version field."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        config_path = service.generate_workflow_config(python_preset, target_dir)

        with config_path.open() as f:
            config = json.load(f)
        assert config["version"] == "1.0"

    def test_config_contains_schema(self, tmp_path: Path, python_preset: LanguagePreset) -> None:
        """Test generated config contains $schema field."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        config_path = service.generate_workflow_config(python_preset, target_dir)

        with config_path.open() as f:
            config = json.load(f)
        assert "$schema" in config
        assert "workflow-config.schema.json" in config["$schema"]

    def test_config_contains_workflow_settings(
        self, tmp_path: Path, python_preset: LanguagePreset
    ) -> None:
        """Test generated config contains default workflow settings."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        config_path = service.generate_workflow_config(python_preset, target_dir)

        with config_path.open() as f:
            config = json.load(f)
        assert "workflow" in config
        assert config["workflow"]["tdd_required"] is True
        assert config["workflow"]["quality_gate_required"] is True
        assert config["workflow"]["auto_report"] is True

    def test_different_preset_generates_different_language(
        self, tmp_path: Path, typescript_preset: LanguagePreset
    ) -> None:
        """Test different preset generates config with different language."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        config_path = service.generate_workflow_config(typescript_preset, target_dir)

        with config_path.open() as f:
            config = json.load(f)
        assert config["language"] == "typescript"
        assert config["quality"]["lint"] == "eslint ."


class TestGenerateGitConventions:
    """Tests for generate_git_conventions method."""

    def test_generates_file(self, tmp_path: Path) -> None:
        """Test git-conventions.md file is created."""
        service = TemplateService()
        target_dir = tmp_path / ".claude"

        result = service.generate_git_conventions(target_dir)

        assert result.exists()
        assert result.name == "git-conventions.md"
        assert result.parent == target_dir

    def test_creates_target_directory(self, tmp_path: Path) -> None:
        """Test target directory is created if not exists."""
        service = TemplateService()
        target_dir = tmp_path / "nested" / "path" / ".claude"

        service.generate_git_conventions(target_dir)

        assert target_dir.exists()

    def test_copies_from_template(self, tmp_path: Path) -> None:
        """Test copies content from template file when available."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_content = "# Custom Git Conventions\n\nCustom content here."
        (templates_dir / "git-conventions.md").write_text(template_content)

        service = TemplateService(templates_dir=templates_dir)
        target_dir = tmp_path / ".claude"

        result = service.generate_git_conventions(target_dir)

        assert result.read_text() == template_content

    def test_raises_error_when_template_missing(self, tmp_path: Path) -> None:
        """Test raises FileNotFoundError when template file is missing."""
        templates_dir = tmp_path / "empty_templates"
        templates_dir.mkdir()

        service = TemplateService(templates_dir=templates_dir)
        target_dir = tmp_path / ".claude"

        with pytest.raises(FileNotFoundError, match="Template file not found"):
            service.generate_git_conventions(target_dir)
