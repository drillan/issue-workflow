"""Update command for issue-workflow CLI."""

from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.models.update import FileChangeType, UpdateResult
from issue_workflow.services.hachimoku_version import (
    check_hachimoku_version,
    format_upgrade_hint,
)
from issue_workflow.services.template import SourceDirectoryNotFoundError, TemplateService

app = typer.Typer(
    help="Update skills and agents to latest version",
    invoke_without_command=True,
)

# Exit codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_NOT_INITIALIZED = 2


def _display_changes(result: UpdateResult, category: str, dry_run: bool) -> None:
    """Display changes for a category (skills or agents).

    Args:
        result: UpdateResult containing changes
        category: "Skills" or "Agents"
        dry_run: Whether this is a dry-run
    """
    changes = result.skills_changes if category == "Skills" else result.agents_changes

    if not changes:
        return

    ui.console.print(f"\n[bold]{category}:[/bold]")
    suffix = " (would be)" if dry_run else ""

    for change in changes:
        name = change.path.name
        if change.change_type == FileChangeType.ADDED:
            ui.print_added(f"{name}{suffix} added")
        elif change.change_type == FileChangeType.UPDATED:
            ui.print_updated(f"{name}{suffix} updated")
        # Note: DELETED type is no longer generated - unmanaged files are ignored (#15)


def _display_summary(result: UpdateResult) -> None:
    """Display summary of changes.

    Args:
        result: Combined UpdateResult
    """
    parts: list[str] = []

    if result.added_count > 0:
        parts.append(f"{result.added_count} added")
    if result.updated_count > 0:
        parts.append(f"{result.updated_count} updated")

    if parts:
        action = "Would update" if result.dry_run else "Updated"
        ui.console.print(f"\n{action}: {', '.join(parts)}")
    else:
        ui.print_info("Everything is up to date")

    if result.dry_run:
        ui.print_info("No changes were made (dry-run mode)")


def _display_errors(result: UpdateResult) -> None:
    """Display error messages.

    Args:
        result: UpdateResult containing errors
    """
    if not result.has_errors:
        return

    ui.print_error("Some files could not be updated:")
    for path, error in result.errors:
        ui.console.print(f"  - {path.name}: {error}")


def _display_hachimoku_hint() -> None:
    """Check and display hachimoku upgrade hint if a newer version is available.

    This is a best-effort check. Any failure is silently ignored
    so it never affects the update command's exit code or output.
    """
    try:
        version_result = check_hachimoku_version()
    except Exception:
        return

    if version_result is None or not version_result.update_available:
        return

    ui.console.print()
    ui.print_info(format_upgrade_hint(version_result))


def _run_update(dry_run: bool = False) -> None:
    """Run the update command logic.

    Args:
        dry_run: If True, only show what would be changed
    """
    project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"

    # Check .claude directory exists
    if not claude_dir.exists():
        ui.print_error(
            "Project not initialized\n\n"
            "The .claude/ directory does not exist.\n"
            "Run 'issue-workflow init' first to initialize the project."
        )
        raise typer.Exit(EXIT_NOT_INITIALIZED)

    # Display mode indicator
    if dry_run:
        ui.print_info("[DRY-RUN] Calculating changes...")
    else:
        ui.print_info("Updating skills and agents...")

    # Run updates
    template_service = TemplateService()

    skills_result = template_service.update_skills(claude_dir, dry_run=dry_run)
    agents_result = template_service.update_agents(claude_dir, dry_run=dry_run)

    # Combine results
    combined_result = UpdateResult(
        skills_changes=skills_result.skills_changes,
        agents_changes=agents_result.agents_changes,
        errors=skills_result.errors + agents_result.errors,
        dry_run=dry_run,
    )

    # Display results
    _display_changes(combined_result, "Skills", dry_run)
    _display_changes(combined_result, "Agents", dry_run)
    _display_summary(combined_result)
    _display_errors(combined_result)

    # Check hachimoku version (best-effort, never affects exit code)
    _display_hachimoku_hint()

    # Set exit code
    if combined_result.has_errors:
        raise typer.Exit(EXIT_GENERAL_ERROR)


@app.callback(invoke_without_command=True)
def update(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would be changed without making changes",
        ),
    ] = False,
) -> None:
    """Update skills and agents to the latest version.

    Updates .claude/skills and .claude/agents directories
    with the latest files from the issue-workflow toolkit.

    Existing files will be overwritten with newer versions.
    Files that exist in your project but not in the toolkit
    will be silently ignored.
    """
    try:
        _run_update(dry_run)
    except KeyboardInterrupt:
        ui.print_info("Update cancelled")
        raise typer.Exit(EXIT_GENERAL_ERROR) from None
    except SourceDirectoryNotFoundError as e:
        ui.print_error(
            f"Installation corrupted: {e}\n\n"
            "Try reinstalling with: uv pip install --force-reinstall issue-workflow"
        )
        raise typer.Exit(EXIT_GENERAL_ERROR) from None
