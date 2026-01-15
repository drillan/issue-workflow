"""Preset loader service."""

import json
from pathlib import Path

from issue_workflow.models.preset import LanguageName, LanguagePreset


class PresetNotFoundError(Exception):
    """Raised when a preset is not found."""

    pass


class PresetLoader:
    """Service for loading language presets."""

    def __init__(self, presets_dir: Path | None = None) -> None:
        """Initialize preset loader.

        Args:
            presets_dir: Directory containing preset JSON files.
                        Defaults to package presets directory.
        """
        if presets_dir is None:
            presets_dir = Path(__file__).parent.parent / "presets"
        self.presets_dir = presets_dir

    def load(self, language: str | LanguageName) -> LanguagePreset:
        """Load a language preset.

        Args:
            language: Language name or enum value

        Returns:
            LanguagePreset for the specified language

        Raises:
            PresetNotFoundError: If preset file does not exist
            ValueError: If preset file contains invalid data
        """
        language_str = language.value if isinstance(language, LanguageName) else language.lower()

        # Validate language name
        try:
            LanguageName(language_str)
        except ValueError as e:
            valid_languages = [lang.value for lang in LanguageName]
            raise PresetNotFoundError(
                f"Invalid language preset: {language_str}. "
                f"Valid options: {', '.join(valid_languages)}"
            ) from e

        preset_path = self.presets_dir / f"{language_str}.json"

        if not preset_path.exists():
            raise PresetNotFoundError(f"Preset file not found: {preset_path}")

        try:
            with preset_path.open() as f:
                data = json.load(f)
            return LanguagePreset(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in preset file: {preset_path}") from e

    def list_available(self) -> list[str]:
        """List available language presets.

        Returns:
            List of available preset names
        """
        return [lang.value for lang in LanguageName]

    def get_display_names(self) -> dict[str, str]:
        """Get mapping of language names to display names.

        Returns:
            Dictionary mapping language name to display name
        """
        display_names: dict[str, str] = {}
        for lang in LanguageName:
            try:
                preset = self.load(lang)
                display_names[lang.value] = preset.display_name
            except (PresetNotFoundError, ValueError):
                display_names[lang.value] = lang.value.capitalize()
        return display_names
