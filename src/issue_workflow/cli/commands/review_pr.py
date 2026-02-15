"""Review-pr subcommand for issue-workflow CLI."""

import subprocess
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.cli.commands._common import EXIT_SUCCESS, log_execution, on_tool_use
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    HACHIMOKU_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.pr_detector import detect_pr_number

COMMAND_NAME: str = "review-pr"


def _run_review_pr(
    pr_number: int | None,
    review_only: bool,
    respond_only: bool,
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the review-pr command logic.

    Args:
        pr_number: PR number (None for auto-detection).
        review_only: Run only hachimoku review.
        respond_only: Run only respond-review.
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 for success, non-zero for failure).

    Raises:
        typer.Exit: If --review-only and --respond-only are both specified.
    """
    # Mutual exclusion check
    if review_only and respond_only:
        ui.print_error("--review-only and --respond-only are mutually exclusive.")
        raise typer.Exit(code=1)

    # Conditional dependency check
    deps = []
    if not respond_only:
        deps.append(HACHIMOKU_DEPENDENCY)
    if not review_only:
        deps.append(CLAUDE_DEPENDENCY)
    if pr_number is None:
        deps.append(GH_DEPENDENCY)
    check_dependencies(deps)

    # PR number detection
    resolved_pr = detect_pr_number(pr_number)

    # Console output
    mode_suffix = " (verbose mode)" if verbose else ""
    ui.console.print(f"\\[review-pr] Starting...{mode_suffix}")

    # Phase 1: hachimoku review (unless --respond-only)
    if not respond_only:
        try:
            hachimoku_result = subprocess.run(
                ["8moku", str(resolved_pr)],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as e:
            ui.print_error(f"Failed to execute 8moku: {e}")
            ui.console.print("\\[review-pr] Done. (exit_code=1)")
            return 1

        if hachimoku_result.stdout:
            ui.console.print(hachimoku_result.stdout.rstrip())
        if hachimoku_result.stderr:
            ui.console.print(hachimoku_result.stderr.rstrip())

        if hachimoku_result.returncode != EXIT_SUCCESS:
            ui.console.print(f"\\[review-pr] Done. (exit_code={hachimoku_result.returncode})")
            return hachimoku_result.returncode

    # Phase 2: respond-review via claude (unless --review-only)
    if not review_only:
        runner = ClaudeRunner()
        result = runner.run(
            f"/respond-review {resolved_pr}",
            cwd=None,
            timeout_seconds=timeout,
            verbose=verbose,
            on_tool_use=on_tool_use if verbose else None,
        )

        log_execution(COMMAND_NAME, {"pr_number": resolved_pr}, result, timeout)

        ui.console.print(f"\\[review-pr] Done. (exit_code={result.exit_code})")
        return result.exit_code

    # review-only path: 8moku succeeded
    ui.console.print(f"\\[review-pr] Done. (exit_code={EXIT_SUCCESS})")
    return EXIT_SUCCESS


def review_pr(
    pr_number: Annotated[
        int | None,
        typer.Argument(help="PR number (auto-detected from current branch if omitted)"),
    ] = None,
    review_only: Annotated[
        bool,
        typer.Option("--review-only", help="Run hachimoku review only (skip respond-review)"),
    ] = False,
    respond_only: Annotated[
        bool,
        typer.Option("--respond-only", help="Run respond-review only (skip hachimoku review)"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show tool calls in real-time (stream-json)"),
    ] = False,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Timeout in seconds for claude -p execution"),
    ] = DEFAULT_TIMEOUT_SECONDS,
) -> None:
    """Review a PR with hachimoku and respond to review findings.

    Executes 8moku for code review, then /respond-review skill via claude -p.

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_review_pr(
        pr_number=pr_number,
        review_only=review_only,
        respond_only=respond_only,
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
