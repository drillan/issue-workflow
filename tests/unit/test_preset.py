"""Unit tests for preset loading."""

import json
from pathlib import Path

import pytest

from issue_workflow.models.config import QualityCommands
from issue_workflow.models.preset import FileTemplate, LanguageName, LanguagePreset


class TestLanguageName:
    """Tests for LanguageName enum."""

    def test_all_languages_defined(self) -> None:
        """Test all expected languages are defined."""
        expected = {"python", "typescript", "go", "rust", "generic"}
        actual = {lang.value for lang in LanguageName}
        assert actual == expected

    def test_language_values(self) -> None:
        """Test language enum values."""
        assert LanguageName.PYTHON.value == "python"
        assert LanguageName.TYPESCRIPT.value == "typescript"
        assert LanguageName.GO.value == "go"
        assert LanguageName.RUST.value == "rust"
        assert LanguageName.GENERIC.value == "generic"


class TestFileTemplate:
    """Tests for FileTemplate model."""

    def test_valid_file_template(self) -> None:
        """Test creating valid file template."""
        template = FileTemplate(path="workflow-config.json", template="workflow-config.json.j2")
        assert template.path == "workflow-config.json"
        assert template.template == "workflow-config.json.j2"


class TestLanguagePreset:
    """Tests for LanguagePreset model."""

    def test_valid_preset(self) -> None:
        """Test creating valid language preset."""
        preset = LanguagePreset(
            name=LanguageName.PYTHON,
            display_name="Python",
            quality=QualityCommands(
                lint="uv run ruff check --fix .",
                format="uv run ruff format .",
                typecheck="uv run mypy .",
                test="uv run pytest",
                all="uv run ruff check --fix . && uv run ruff format . && uv run mypy .",
            ),
            files=[
                FileTemplate(path="workflow-config.json", template="workflow-config.json.j2"),
                FileTemplate(path="git-conventions.md", template="git-conventions.md"),
            ],
        )
        assert preset.name == LanguageName.PYTHON
        assert preset.display_name == "Python"
        assert len(preset.files) == 2


class TestPresetJsonFiles:
    """Tests for preset JSON files."""

    @pytest.fixture
    def presets_dir(self) -> Path:
        """Get presets directory path."""
        return Path(__file__).parent.parent.parent / "src" / "issue_workflow" / "presets"

    @pytest.mark.parametrize(
        "preset_name",
        ["python", "typescript", "go", "rust", "generic"],
    )
    def test_preset_file_exists(self, presets_dir: Path, preset_name: str) -> None:
        """Test that preset file exists."""
        preset_file = presets_dir / f"{preset_name}.json"
        assert preset_file.exists(), f"Preset file {preset_file} does not exist"

    @pytest.mark.parametrize(
        "preset_name",
        ["python", "typescript", "go", "rust", "generic"],
    )
    def test_preset_file_valid_json(self, presets_dir: Path, preset_name: str) -> None:
        """Test that preset file contains valid JSON."""
        preset_file = presets_dir / f"{preset_name}.json"
        with preset_file.open() as f:
            data = json.load(f)
        assert "name" in data
        assert "display_name" in data
        assert "quality" in data
        assert "files" in data

    @pytest.mark.parametrize(
        "preset_name",
        ["python", "typescript", "go", "rust", "generic"],
    )
    def test_preset_can_be_loaded(self, presets_dir: Path, preset_name: str) -> None:
        """Test that preset can be loaded into model."""
        preset_file = presets_dir / f"{preset_name}.json"
        with preset_file.open() as f:
            data = json.load(f)
        preset = LanguagePreset(**data)
        assert preset.name.value == preset_name
