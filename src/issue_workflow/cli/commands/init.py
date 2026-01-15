"""Init command for issue-workflow CLI."""

from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.models.config import DDDSettings, DocumentationSettings
from issue_workflow.models.preset import LanguagePreset
from issue_workflow.services.github import check_gh_availability
from issue_workflow.services.preset_loader import PresetLoader, PresetNotFoundError
from issue_workflow.services.template import TemplateService

app = typer.Typer(
    help="Initialize Issue Workflow in current project",
    invoke_without_command=True,
)

# Exit codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_INVALID_ARGUMENT = 2
EXIT_CONFIG_EXISTS = 3


def get_language_choices() -> list[tuple[str, str]]:
    """Get language choices for selection menu."""
    loader = PresetLoader()
    display_names = loader.get_display_names()
    return [(lang, display_names[lang]) for lang in loader.list_available()]


def _get_documentation_settings(
    preset: LanguagePreset,
    non_interactive: bool,
) -> DocumentationSettings:
    """Get documentation settings from user or preset defaults.

    Args:
        preset: Language preset with default documentation settings
        non_interactive: Skip interactive prompts

    Returns:
        Documentation settings (from user input or preset defaults)
    """
    if non_interactive:
        return preset.documentation

    # Documentation paths
    paths = ui.input_list(
        "Documentation paths",
        preset.documentation.paths,
    )

    # Changelog file
    changelog_default = preset.documentation.changelog or "CHANGELOG.md"
    changelog = ui.input_text("CHANGELOG file", changelog_default)

    # DDD enabled
    ddd_enabled = ui.confirm(
        "Enable DDD workflow?",
        default=preset.documentation.ddd.enabled,
    )

    return DocumentationSettings(
        paths=paths,
        changelog=changelog,
        ddd=DDDSettings(
            enabled=ddd_enabled,
            retcon_writing=preset.documentation.ddd.retcon_writing,
        ),
    )


@app.callback(invoke_without_command=True)
def init(
    language: Annotated[
        str | None,
        typer.Option(
            "--language",
            "-l",
            help="Language preset: python, typescript, go, rust, generic",
        ),
    ] = None,
    non_interactive: Annotated[
        bool,
        typer.Option(
            "--non-interactive",
            help="Skip interactive prompts (requires --language)",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing configuration",
        ),
    ] = False,
) -> None:
    """Initialize Issue Workflow in the current project."""
    try:
        _run_init(language, non_interactive, force)
    except KeyboardInterrupt:
        ui.print_info("Initialization cancelled")
        raise typer.Exit(EXIT_GENERAL_ERROR) from None


def _run_init(language: str | None, non_interactive: bool, force: bool) -> None:
    """Run the init command logic."""
    project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"
    config_file = claude_dir / "workflow-config.json"

    # Check gh CLI availability
    gh_available, gh_message = check_gh_availability()
    if not gh_available:
        ui.print_error(gh_message)
        raise typer.Exit(EXIT_GENERAL_ERROR)

    # Check existing config
    if config_file.exists() and not force:
        if non_interactive:
            ui.print_error(
                "Configuration file already exists\n\n"
                f"{config_file} already exists.\n"
                "Use --force option to overwrite."
            )
            raise typer.Exit(EXIT_CONFIG_EXISTS)
        else:
            if not ui.confirm("Configuration file already exists. Overwrite?", default=False):
                ui.print_info("Initialization cancelled")
                raise typer.Exit(EXIT_SUCCESS)

    # Get language selection
    if language is None:
        if non_interactive:
            ui.print_error(
                "Language preset is required\n\n"
                "Please specify a language with --language option.\n\n"
                "Example: issue-workflow init --language python --non-interactive"
            )
            raise typer.Exit(EXIT_INVALID_ARGUMENT)
        else:
            # Interactive selection
            choices = get_language_choices()
            language = ui.select_option("Select language preset", choices)

    # Validate and load preset
    loader = PresetLoader()
    try:
        preset = loader.load(language)
    except PresetNotFoundError as e:
        ui.print_error(
            f"Invalid language preset: {language}\n\nValid options: {', '.join(loader.list_available())}"
        )
        raise typer.Exit(EXIT_INVALID_ARGUMENT) from e

    # Get documentation settings
    documentation = _get_documentation_settings(preset, non_interactive)

    # Generate config files
    template_service = TemplateService()
    ui.print_info(f"Initializing with {preset.display_name} preset...")

    generated_files = template_service.generate_all(preset, claude_dir, documentation)
    for path in generated_files:
        ui.print_success(f"Created {path.relative_to(project_dir)}")

    ui.print_success("Issue Workflow initialized successfully!")
    ui.print_info("Run 'claude' to start using the workflow commands")
