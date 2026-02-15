# Quickstart: Workflow Subcommands

**Feature Branch**: `011-workflow-subcommands`
**Date**: 2026-02-15

## Prerequisites

```bash
# Install issue-workflow
uv tool install issue-workflow

# Initialize project (creates .claude/skills/)
issue-workflow init

# Required external tools
# - claude: https://www.anthropic.com/claude-code
# - gh: https://cli.github.com/
# - 8moku: uv tool install hachimoku
```

## Quick Usage

### Single Issue Workflow (individual commands)

```bash
# 1. Start working on an issue
issue-workflow start-issue 199

# 2. Create a PR (commit + push + PR)
issue-workflow create-pr

# 3. Review the PR (hachimoku + respond)
issue-workflow review-pr

# 4. Push review fixes
issue-workflow push-changes

# 5. Respond to human review comments
issue-workflow respond-comments

# 6. Merge the PR
issue-workflow merge-pr
```

### Full Automated Workflow

```bash
# Run all steps automatically
issue-workflow run 199

# With worktree isolation
issue-workflow run 199 --worktree
```

### Verbose Mode (see tool calls in real-time)

```bash
issue-workflow start-issue 199 -v
issue-workflow run 199 -v --worktree
```

### With Worktree

```bash
# Create worktree + start issue
issue-workflow start-issue 199 --worktree

# Work in worktree...
cd ../project-feat-199-description/
issue-workflow create-pr
issue-workflow review-pr
issue-workflow push-changes

# Merge from main repo
cd ../project/
issue-workflow merge-pr
```

### Explicit PR Number

```bash
issue-workflow review-pr 300
issue-workflow respond-comments 300
issue-workflow merge-pr 300
```

### Review Options

```bash
# Only run hachimoku review (skip respond)
issue-workflow review-pr --review-only

# Only respond to existing review (skip hachimoku)
issue-workflow review-pr --respond-only
```

## Logs

All executions are logged to `.issue-workflow/logs/`:

```bash
ls .issue-workflow/logs/2026-02-15/
# start-issue-199-2026-02-15T10-30-00.jsonl   # Issue #199
# create-pr-2026-02-15T10-45-00.jsonl          # PR番号は作成前なので省略
# review-pr-201-2026-02-15T11-00-00.jsonl      # PR #201 (Issue #199 から作成)
```

## Developer Guide (for contributors)

### Architecture

```
Subcommand (Typer CLI)
  → DependencyChecker (validate external tools)
  → Pre-processing (worktree, PR detection)
  → ClaudeRunner.run(prompt, cwd=..., verbose=...)
  → ExecutionLogger.log(entry)
  → Exit with appropriate code
```

### Adding a New Subcommand

1. Create `src/issue_workflow/cli/commands/<name>.py`
2. Define Typer app with `@app.command()`
3. Register in `cli/main.py` via `_register_commands()`
4. Add tests in `tests/unit/` and `tests/integration/`

### Running Tests

```bash
uv run pytest tests/unit/test_claude_runner.py -v
uv run pytest tests/integration/test_start_issue_command.py -v
uv run pytest  # all tests
```

### Quality Checks

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```
