# Issue Workflow Toolkit

English | [日本語](README.ja.md)

GitHub Issue-driven development workflow toolkit for Claude Code. Automates and streamlines the entire workflow from starting an issue to merging a PR.

## Features

- **TDD-Enforced Workflow** - Ensures test-first development with the Red-Green-Refactor cycle
- **Quality Gate** - Automatic lint, format, and type checking before commits
- **Auto Progress Reporting** - Automatically posts progress updates to GitHub Issues
- **Multi-Language Support** - Pre-configured presets for Python, TypeScript, Go, Rust, and Generic

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)
- [gh CLI](https://cli.github.com/) (GitHub CLI)
- [Claude Code](https://www.anthropic.com/claude-code) CLI
- [hachimoku](https://github.com/drillan/hachimoku) (for `review-pr` / `run` subcommands)

## Installation

```bash
uv tool install git+https://github.com/drillan/issue-workflow.git
```

## Quick Start

```bash
# 1. Initialize workflow configuration in your project
issue-workflow init

# 2. Or initialize with a specific language preset
issue-workflow init --language python
```

After initialization, use Claude Code slash commands to manage your workflow:

```
/start-issue 123      # Start working on Issue #123
/review-pr-comments   # Address PR review comments
/merge-pr 456         # Merge PR #456
```

## Updating

When a new version is released, update the toolkit and sync skills/agents:

```bash
# 1. Update the toolkit
uv tool install --reinstall git+https://github.com/drillan/issue-workflow.git

# 2. Update skills and agents in your project
issue-workflow update
```

> **Note**: `uv tool install` does nothing if the package is already installed.
> The `--reinstall` flag fetches the latest code from the remote repository and reinstalls it.

The `update` command also checks if a newer version of [hachimoku](https://github.com/drillan/hachimoku) is available and displays an upgrade hint:

```
ℹ hachimoku の新しいバージョンが利用可能です (現在: 0.0.2, 最新: 0.0.3)
  アップグレード:   uv tool install --reinstall git+https://github.com/drillan/hachimoku.git
  エージェント更新: 8moku init --force
```

Use `--dry-run` to preview changes before applying:

```bash
issue-workflow update --dry-run
```

## CLI Commands

### Setup Commands

| Command | Description |
|---------|-------------|
| `issue-workflow init` | Initialize Issue Workflow in project |
| `issue-workflow init --language <lang>` | Initialize with language preset |
| `issue-workflow init --non-interactive` | Initialize without interactive prompts (CI/CD) |
| `issue-workflow update` | Update skills and agents to latest version |
| `issue-workflow update --dry-run` | Show what would be updated without making changes |
| `issue-workflow --version` | Show version |
| `issue-workflow --help` | Show help |

### Workflow Subcommands

Automate the development workflow via `claude -p` subprocess execution. Each subcommand logs its results to `.issue-workflow/logs/` in JSONL format.

| # | Command | Description |
|---|---------|-------------|
| 1 | `issue-workflow start-issue <number>` | Start working on an issue (executes `/start-issue` skill) |
| 2 | `issue-workflow create-pr` | Commit, push, and create PR (executes `/commit-push-pr` skill) |
| 3 | `issue-workflow review-pr [number]` | Run hachimoku review + respond to findings |
| 4 | `issue-workflow push-changes` | Push review fixes (commit + push, skip PR creation) |
| 5 | `issue-workflow respond-comments [number]` | Respond to human PR review comments |
| 6 | `issue-workflow merge-pr [number]` | Wait for CI checks, then merge PR |
| 7 | `issue-workflow run <number>` | Run full workflow (steps 1-6 sequentially) |

**Common options** (all workflow subcommands):

| Option | Description |
|--------|-------------|
| `--verbose` / `-v` | Show tool calls in real-time (stream-json) |
| `--timeout <seconds>` | Timeout for claude -p execution (default: 3600) |
| `--help` / `-h` | Show usage |

**Additional options**:

| Command | Option | Description |
|---------|--------|-------------|
| `start-issue` | `--worktree` | Create worktree and run skill there |
| `review-pr` | `--review-only` | Run hachimoku review only (skip respond) |
| `review-pr` | `--respond-only` | Run respond-review only (skip hachimoku) |
| `run` | `--worktree` | Create worktree and run full workflow there |

#### Full Automated Workflow

```bash
# Run all steps automatically for Issue #199
issue-workflow run 199

# With worktree isolation
issue-workflow run 199 --worktree
```

#### Individual Commands

```bash
# Step by step
issue-workflow start-issue 199
issue-workflow create-pr
issue-workflow review-pr
issue-workflow push-changes
issue-workflow respond-comments    # For human review comments
issue-workflow merge-pr
```

## Slash Commands

Use these commands within Claude Code. Listed in recommended workflow order:

| # | Command | Description | Arguments |
|---|---------|-------------|-----------|
| 1 | `/add-worktree` | Create a new worktree for an Issue (optional) | `<issue-number>` |
| 2 | `/start-issue` | Load Issue, create branch, and develop implementation plan | `<issue-number>` |
| 3 | `/commit-push-pr` | Commit, push, and create PR | - |
| 4 | `/respond-review` | Respond to hachimoku review findings | `[pr-number]` (optional) |
| 5 | `/review-pr-comments` | Review and respond to PR review comments | `[pr-number]` (optional) |
| 6 | `/merge-pr` | Wait for CI checks, then merge PR | `<pr-number>` |

## Auto-Activated Skills

These skills are automatically triggered during appropriate contexts:

| # | Skill | Description | Activation Timing |
|---|-------|-------------|-------------------|
| 1 | `tdd-workflow` | Enforces TDD workflow (Red-Green-Refactor cycle) | Implementation start |
| 2 | `code-quality-gate` | Runs quality checks before commits | Pre-commit (required to pass) |
| 3 | `issue-reporter` | Posts progress updates to Issues | Planning phase, problem detection |
| 4 | `doc-updater` | Detects changes requiring documentation updates | API changes (optional) |

## Language Presets

Available presets with pre-configured quality commands:

| Preset | Quality Tools |
|--------|---------------|
| `python` | ruff, mypy, pytest |
| `typescript` | npm run lint/format/typecheck (typically eslint, prettier, tsc) |
| `go` | golangci-lint, go fmt, go vet |
| `rust` | clippy, rustfmt, cargo check |
| `generic` | Customizable |

## Configuration

### Workflow Config (`.claude/workflow-config.json`)

```json
{
  "version": "1.0",
  "language": "python",
  "quality": {
    "lint": "uv run ruff check --fix .",
    "format": "uv run ruff format .",
    "typecheck": "uv run mypy .",
    "test": "uv run pytest",
    "all": "uv run ruff check --fix . && uv run ruff format . && uv run mypy ."
  },
  "workflow": {
    "tdd_required": true,
    "quality_gate_required": true,
    "auto_report": true
  },
  "documentation": {
    "paths": ["README.md", "docs/"],
    "changelog": "CHANGELOG.md",
    "ddd": {
      "enabled": true,
      "retcon_writing": true
    }
  },
  "$schema": "https://raw.githubusercontent.com/drillan/issue-workflow/main/schemas/workflow-config.schema.json"
}
```

### Documentation Settings

The `documentation` section configures documentation paths and DDD (Documentation-Driven Development) workflow:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `paths` | `string[]` | `["README.md", "docs/"]` | Documentation file/directory paths to maintain |
| `changelog` | `string` | `"CHANGELOG.md"` | Changelog file path |
| `ddd.enabled` | `boolean` | `true` | Enable DDD workflow |
| `ddd.retcon_writing` | `boolean` | `true` | Enforce retcon writing style (write docs as if feature exists) |

During `issue-workflow init`, you can customize these settings interactively or use preset defaults with `--non-interactive`.

### Git Conventions (`.claude/git-conventions.md`)

Defines branch naming and commit message conventions:

- Branch format: `<type>/<issue-number>-<description>`
- Types: `feat/`, `fix/`, `refactor/`, `docs/`, `test/`, `chore/`
- Commit format: Conventional Commits

## Development

### Setup

```bash
git clone https://github.com/drillan/issue-workflow.git
cd issue-workflow
uv sync
```

### Running Tests

```bash
uv run pytest
```

### Quality Checks

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```

### Docker Development Environment

A Docker environment is available for clean, reproducible testing.

**Prerequisites:** Docker, Docker Compose, [gh CLI](https://cli.github.com/) (on host)

**Build the image:**

```bash
make docker-build
```

**Authentication:**

- **GitHub CLI** — Automatically injected via `GH_TOKEN` from the host's `gh auth token`
- **Claude Code** — Run `claude` on first launch and complete the OAuth login flow. Credentials are persisted in a named Docker volume (`claude-auth`) and survive `--rm` container removal

**Usage:**

```bash
make docker-dev       # Interactive development shell
make docker-test      # Run pytest
make docker-quality   # Run ruff + mypy
```

**Reset Claude Code authentication:**

```bash
docker volume rm issue-workflow_claude-auth
```

## Troubleshooting

### gh CLI Authentication Error

If you encounter authentication errors with `gh`:

```bash
gh auth login
```

### Overwriting Existing Configuration

To reinitialize configuration in an existing project:

```bash
issue-workflow init --force
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `gh: command not found` | Install [GitHub CLI](https://cli.github.com/) |
| `uv: command not found` | Install [uv](https://docs.astral.sh/uv/) |
| Branch creation failed | Check for uncommitted changes with `git status` |
| Permission denied on Issue | Verify repository access with `gh repo view` |

## License

MIT
