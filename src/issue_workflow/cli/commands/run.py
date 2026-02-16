"""Run subcommand for full workflow execution."""

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from issue_workflow.cli import ui
from issue_workflow.cli.commands._common import EXIT_SUCCESS, log_execution, on_tool_use
from issue_workflow.cli.commands.push_changes import PUSH_CHANGES_PROMPT
from issue_workflow.cli.commands.start_issue import _prepare_worktree
from issue_workflow.models.workflow_context import WorkflowContext
from issue_workflow.services.claude_runner import DEFAULT_TIMEOUT_SECONDS, ClaudeRunner
from issue_workflow.services.dependency_checker import (
    CLAUDE_DEPENDENCY,
    GH_DEPENDENCY,
    HACHIMOKU_DEPENDENCY,
    check_dependencies,
)
from issue_workflow.services.pr_detector import detect_pr_number

COMMAND_NAME: str = "run"


def _run_step(
    ctx: WorkflowContext,
    step_label: str,
    command_name: str,
    prompt: str,
    log_args: dict[str, str | int | bool],
    *,
    cwd: Path | None = None,
    verbose: bool = False,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> bool:
    """Execute a single Claude skill step and update context.

    Args:
        ctx: Workflow context to update with step result.
        step_label: Step label for console output (e.g., "Step 1/4: start-issue").
        command_name: Command name for logging.
        prompt: Prompt text for claude -p.
        log_args: Arguments dict for the execution log entry.
        cwd: Working directory for subprocess execution.
        verbose: If True, use stream-json format with real-time output.
        timeout: Timeout in seconds for claude -p execution.

    Returns:
        True if step succeeded, False if failed.
    """
    mode_suffix = " (verbose mode)" if verbose else ""
    ui.console.print(f"\\[{COMMAND_NAME}] {step_label} Starting...{mode_suffix}")

    runner = ClaudeRunner()
    result = runner.run(
        prompt,
        cwd=cwd,
        timeout_seconds=timeout,
        verbose=verbose,
        on_tool_use=on_tool_use if verbose else None,
    )

    ctx.step_results.append(result)
    log_execution(command_name, log_args, result, timeout)

    ui.console.print(f"\\[{COMMAND_NAME}] {step_label} Done. (exit_code={result.exit_code})")

    return result.exit_code == EXIT_SUCCESS and not result.is_error


def _print_failure(step_name: str) -> None:
    """Print failure message with step name.

    Args:
        step_name: Name of the failed step.
    """
    ui.print_error(
        f"Workflow stopped at '{step_name}'. "
        "Use individual subcommands to retry from the failed step."
    )


def _run_workflow(
    issue_number: int,
    worktree: bool,
    verbose: bool,
    timeout: int,
) -> int:
    """Execute the full workflow.

    Runs all steps sequentially: start-issue -> create-pr ->
    review+respond+push -> merge-pr. Stops on first failure.

    Args:
        issue_number: GitHub Issue number.
        worktree: Whether to use worktree.
        verbose: Whether to show verbose output.
        timeout: Timeout in seconds for claude -p execution.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    check_dependencies([CLAUDE_DEPENDENCY, GH_DEPENDENCY, HACHIMOKU_DEPENDENCY])

    ctx = WorkflowContext(issue_number=issue_number)

    # Step 0 (optional): worktree preparation
    if worktree:
        cwd = _prepare_worktree(issue_number)
        if cwd is None:
            return 1
        ctx.worktree_path = cwd

    # Step 1: start-issue
    if not _run_step(
        ctx,
        "Step 1/4: start-issue",
        "start-issue",
        f"/start-issue {issue_number} --force",
        {"issue_number": issue_number, "worktree": worktree},
        cwd=ctx.cwd_for_skill,
        verbose=verbose,
        timeout=timeout,
    ):
        _print_failure("start-issue")
        return 1

    # Step 2: create-pr
    if not _run_step(
        ctx,
        "Step 2/4: create-pr",
        "create-pr",
        "/commit-push-pr",
        {},
        cwd=ctx.cwd_for_skill,
        verbose=verbose,
        timeout=timeout,
    ):
        _print_failure("create-pr")
        return 1

    # Detect PR number after create-pr
    try:
        pr_number: int = detect_pr_number(cwd=ctx.cwd_for_skill)
    except SystemExit:
        _print_failure("detect-pr")
        return 1
    ctx.pr_number = pr_number

    # Step 3a: hachimoku review (subprocess, no ClaudeResult)
    ui.console.print(f"\\[{COMMAND_NAME}] Step 3/4: review (hachimoku) Starting...")
    try:
        hachimoku_result = subprocess.run(
            ["8moku", str(pr_number)],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        ui.print_error(f"8moku timed out after {timeout} seconds")
        _print_failure("review (hachimoku)")
        return 1
    except OSError as e:
        ui.print_error(f"Failed to execute 8moku: {e}")
        _print_failure("review (hachimoku)")
        return 1

    if hachimoku_result.stdout:
        ui.console.print(hachimoku_result.stdout.rstrip())
    if hachimoku_result.stderr:
        ui.console.print(hachimoku_result.stderr.rstrip())

    ui.console.print(
        f"\\[{COMMAND_NAME}] Step 3/4: review (hachimoku) Done. "
        f"(exit_code={hachimoku_result.returncode})"
    )

    # Step 3b: respond-review
    if not _run_step(
        ctx,
        "Step 3/4: review (respond)",
        "review-pr",
        f"/respond-review {pr_number}",
        {"pr_number": pr_number},
        cwd=ctx.cwd_for_skill,
        verbose=verbose,
        timeout=timeout,
    ):
        _print_failure("review (respond)")
        return 1

    # Step 3c: push-changes
    if not _run_step(
        ctx,
        "Step 3/4: push-changes",
        "push-changes",
        PUSH_CHANGES_PROMPT,
        {"pr_number": pr_number},
        cwd=ctx.cwd_for_skill,
        verbose=verbose,
        timeout=timeout,
    ):
        _print_failure("push-changes")
        return 1

    # Step 4: merge-pr (always from main repo, cwd=None)
    if not _run_step(
        ctx,
        "Step 4/4: merge-pr",
        "merge-pr",
        f"/merge-pr {pr_number}",
        {"pr_number": pr_number},
        cwd=ctx.cwd_for_merge,
        verbose=verbose,
        timeout=timeout,
    ):
        _print_failure("merge-pr")
        return 1

    # All steps succeeded
    ui.console.print(
        f"\\[{COMMAND_NAME}] All steps completed successfully. "
        f"(total_cost=${ctx.total_cost_usd:.4f})"
    )
    return EXIT_SUCCESS


def run(
    issue_number: Annotated[
        int,
        typer.Argument(help="GitHub Issue number"),
    ],
    worktree: Annotated[
        bool,
        typer.Option("--worktree", help="Create worktree and run workflow there"),
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
    """Run full workflow: start-issue -> create-pr -> review+respond+push -> merge-pr.

    Executes all workflow steps sequentially. Stops on first failure.

    \u26a0\ufe0f  Security: This command uses --dangerously-skip-permissions to bypass
    Claude Code's permission checks for automated execution. Only run in
    trusted environments.
    """
    exit_code = _run_workflow(
        issue_number=issue_number,
        worktree=worktree,
        verbose=verbose,
        timeout=timeout,
    )
    if exit_code != EXIT_SUCCESS:
        raise typer.Exit(code=exit_code)
