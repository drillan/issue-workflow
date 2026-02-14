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

When a new version is released, update the toolkit and sync commands/skills:

```bash
# 1. Update the toolkit
uv tool install --reinstall git+https://github.com/drillan/issue-workflow.git

# 2. Update commands and skills in your project
issue-workflow update
```

Use `--dry-run` to preview changes before applying:

```bash
issue-workflow update --dry-run
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `issue-workflow init` | Initialize Issue Workflow in project |
| `issue-workflow init --language <lang>` | Initialize with language preset |
| `issue-workflow init --non-interactive` | Initialize without interactive prompts (CI/CD) |
| `issue-workflow update` | Update commands and skills to latest version |
| `issue-workflow update --dry-run` | Show what would be updated without making changes |
| `issue-workflow --version` | Show version |
| `issue-workflow --help` | Show help |

## Plugin Commands (Slash Commands)

Use these commands within Claude Code. Listed in recommended workflow order:

| # | Command | Description | Arguments |
|---|---------|-------------|-----------|
| 1 | `/add-worktree` | Create a new worktree for an Issue (optional) | `<issue-number>` |
| 2 | `/start-issue` | Load Issue, create branch, and develop implementation plan | `<issue-number>` |
| - | `/commit-push-pr` | Commit, push, and create PR (Official Plugin) | - |
| - | `/pr-review-toolkit:review-pr` | Review PR (Official Plugin) | `<pr-number>` |
| 3 | `/review-pr-comments` | Review and respond to PR review comments | `[pr-number]` (optional) |
| 4 | `/merge-pr` | Wait for CI checks, then merge PR | `<pr-number>` |

### Official Plugin Integration

This toolkit integrates with official Claude Code plugins:

- **commit-commands** - Provides `/commit-push-pr` for streamlined commit, push, and PR creation
- **pr-review-toolkit** - Provides `/pr-review-toolkit:review-pr` for comprehensive PR reviews. Can also be used as a [GitHub Action](https://github.com/marketplace/actions/claude-pr-reviewer) for CI integration.

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
