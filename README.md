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
- [Claude Code](https://claude.ai/claude-code) CLI

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

## CLI Commands

| Command | Description |
|---------|-------------|
| `issue-workflow init` | Initialize Issue Workflow in project |
| `issue-workflow init --language <lang>` | Initialize with language preset |
| `issue-workflow --version` | Show version |
| `issue-workflow --help` | Show help |

## Plugin Commands (Slash Commands)

Use these commands within Claude Code:

| Command | Description |
|---------|-------------|
| `/start-issue <number>` | Load Issue, create branch, and develop implementation plan |
| `/merge-pr <number>` | Wait for CI checks, then merge PR |
| `/add-worktree <number>` | Create a new worktree for an Issue |
| `/review-pr-comments [number]` | Review and respond to PR review comments |

## Auto-Activated Skills

These skills are automatically triggered during appropriate contexts:

| Skill | Description |
|-------|-------------|
| `tdd-workflow` | Enforces TDD workflow (Red-Green-Refactor cycle) |
| `code-quality-gate` | Runs quality checks before commits |
| `issue-reporter` | Posts progress updates to Issues |
| `doc-updater` | Detects changes requiring documentation updates |

## Language Presets

Available presets with pre-configured quality commands:

| Preset | Quality Tools |
|--------|---------------|
| `python` | ruff, mypy, pytest |
| `typescript` | eslint, prettier, tsc |
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
  }
}
```

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
