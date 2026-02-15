"""Service for checking external command dependencies."""

import shutil
from dataclasses import dataclass

import typer

from issue_workflow.cli import ui
from issue_workflow.services.github import check_gh_availability

CLAUDE_INSTALL_URL: str = "https://www.anthropic.com/claude-code"
GH_INSTALL_URL: str = "https://cli.github.com/"
HACHIMOKU_INSTALL_HINT: str = "uv tool install hachimoku"


@dataclass(frozen=True)
class DependencyInfo:
    """External command dependency information."""

    command: str
    install_hint: str
    check_auth: bool


CLAUDE_DEPENDENCY = DependencyInfo(
    command="claude",
    install_hint=CLAUDE_INSTALL_URL,
    check_auth=False,
)

GH_DEPENDENCY = DependencyInfo(
    command="gh",
    install_hint=GH_INSTALL_URL,
    check_auth=True,
)

HACHIMOKU_DEPENDENCY = DependencyInfo(
    command="8moku",
    install_hint=HACHIMOKU_INSTALL_HINT,
    check_auth=False,
)


def check_dependencies(dependencies: list[DependencyInfo]) -> None:
    """Check if all required external commands are available.

    Args:
        dependencies: List of dependency info to check.

    Raises:
        typer.Exit: If any dependency is missing, with install hints.
    """
    missing: list[DependencyInfo] = []

    for dep in dependencies:
        if shutil.which(dep.command) is None:
            missing.append(dep)
            continue

        if dep.check_auth:
            available, message = check_gh_availability()
            if not available:
                ui.print_error(message)
                raise typer.Exit(code=1)

    if missing:
        lines = ["Required commands not found:\n"]
        for dep in missing:
            lines.append(f"  - {dep.command}: {dep.install_hint}")
        ui.print_error("\n".join(lines))
        raise typer.Exit(code=1)
