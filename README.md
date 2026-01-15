# Issue Workflow Toolkit

English | [日本語](README.ja.md)

GitHub Issue-driven development workflow toolkit for Claude Code.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)
- [gh CLI](https://cli.github.com/) (GitHub CLI)

## Installation

```bash
uv pip install -e .
```

## Commands

| Command | Description |
|---------|-------------|
| `issue-workflow init` | Initialize Issue Workflow in project |
| `issue-workflow init --language python` | Initialize with language preset |
| `issue-workflow --version` | Show version |
| `issue-workflow --help` | Show help |

## Usage

```bash
# Initialize workflow configuration
issue-workflow init

# With specific language preset
issue-workflow init --language python
```

## License

MIT
