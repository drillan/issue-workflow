"""Init command for issue-workflow CLI."""

from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.services.github import check_gh_availability
from issue_workflow.services.preset_loader import PresetLoader, PresetNotFoundError
from issue_workflow.services.template import (
    TemplateService,
    check_user_scope_plugin,
    update_settings_json,
)

app = typer.Typer(
    help="Initialize Issue Workflow in current project",
    invoke_without_command=True,
)

PLUGIN_URL = "github:drillan/issue-workflow#plugin"

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
                "設定ファイルが既に存在します\n\n"
                f"{config_file} が既に存在します。\n"
                "上書きするには --force オプションを使用してください。"
            )
            raise typer.Exit(EXIT_CONFIG_EXISTS)
        else:
            if not ui.confirm("設定ファイルが既に存在します。上書きしますか?", default=False):
                ui.print_info("Initialization cancelled")
                raise typer.Exit(EXIT_SUCCESS)

    # Get language selection
    if language is None:
        if non_interactive:
            ui.print_error(
                "言語プリセットが必要です\n\n"
                "--language オプションで言語を指定してください。\n\n"
                "例: issue-workflow init --language python --non-interactive"
            )
            raise typer.Exit(EXIT_INVALID_ARGUMENT)
        else:
            # Interactive selection
            choices = get_language_choices()
            language = ui.select_option("言語プリセットを選択", choices)

    # Validate and load preset
    loader = PresetLoader()
    try:
        preset = loader.load(language)
    except PresetNotFoundError as e:
        ui.print_error(
            f"無効な言語プリセットです: {language}\n\n有効な値: {', '.join(loader.list_available())}"
        )
        raise typer.Exit(EXIT_INVALID_ARGUMENT) from e

    # Generate config files
    template_service = TemplateService()
    ui.print_info(f"Initializing with {preset.display_name} preset...")

    generated_files = template_service.generate_all(preset, claude_dir)
    for path in generated_files:
        ui.print_success(f"Created {path.relative_to(project_dir)}")

    # Update settings.json with plugin
    if not check_user_scope_plugin(PLUGIN_URL):
        settings_path = update_settings_json(claude_dir, PLUGIN_URL)
        ui.print_success(f"Updated {settings_path.relative_to(project_dir)}")
    else:
        ui.print_info("Plugin already installed in user scope, skipping project settings")

    ui.print_success("Issue Workflow initialized successfully!")
    ui.print_info("Run 'claude' to start Claude Code with the workflow plugin")
