"""Interactive UI components for CLI."""

from typing import TypeVar

import readchar
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

T = TypeVar("T")

console = Console()


def select_option(
    title: str,
    options: list[tuple[str, str]],
    default_index: int = 0,
) -> str:
    """Display interactive selection menu.

    Args:
        title: Title to display above options
        options: List of (value, display_label) tuples
        default_index: Default selected index

    Returns:
        Selected option value
    """
    selected = default_index

    while True:
        # Clear screen and draw menu
        console.clear()

        # Build menu content
        lines: list[Text] = []
        for i, (_value, label) in enumerate(options):
            if i == selected:
                line = Text(f"  > {label}", style="bold cyan")
            else:
                line = Text(f"    {label}")
            lines.append(line)

        menu_text = Text("\n").join(lines)
        panel = Panel(
            menu_text,
            title=title,
            subtitle="↑↓: Navigate  Enter: Select",
            border_style="cyan",
        )
        console.print(panel)

        # Handle input
        key = readchar.readkey()

        if key == readchar.key.UP:
            selected = (selected - 1) % len(options)
        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(options)
        elif key == readchar.key.ENTER:
            console.clear()
            return options[selected][0]
        elif key == readchar.key.CTRL_C:
            raise KeyboardInterrupt


def confirm(message: str, default: bool = True) -> bool:
    """Display confirmation prompt.

    Args:
        message: Message to display
        default: Default value if Enter is pressed

    Returns:
        True if confirmed, False otherwise
    """
    default_hint = "[Y/n]" if default else "[y/N]"
    console.print(f"{message} {default_hint} ", end="")

    while True:
        key = readchar.readkey().lower()

        if key == "\r" or key == "\n":
            console.print()
            return default
        elif key == "y":
            console.print("y")
            return True
        elif key == "n":
            console.print("n")
            return False
        elif key == readchar.key.CTRL_C:
            raise KeyboardInterrupt


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]i[/blue] {message}")


def print_added(message: str) -> None:
    """Print message for added item."""
    console.print(f"  [green]+[/green] {message}")


def print_updated(message: str) -> None:
    """Print message for updated item."""
    console.print(f"  [yellow]~[/yellow] {message}")


def print_deleted(message: str) -> None:
    """Print message for deleted item (warning)."""
    console.print(f"  [red]-[/red] {message}")
