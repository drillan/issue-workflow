# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-02-19

### Fixed

- `ClaudeResult.is_error` flag silently ignored, causing errors to be treated as success (#108)
- Missing timeout handling for 8moku subprocess in `review-pr` command (#109)
- Potential deadlock in `_run_verbose()` due to unread `stderr=subprocess.PIPE` (#110)
- Non-atomic directory replacement in `update_skills` risking data loss on `copytree` failure (#111)
- Incomplete exception handling: `OSError` wrapping in `git.py`, uncaught `GitError` in `detect_pr_number()`, unhandled `OSError` in `copy_hachimoku_to_worktree()` (#112)

### Changed

- Improve type and model design consistency: remove `else 0` fallback, use `tuple` instead of `list` in frozen dataclasses, unify `str` inheritance for enums (#113)
- Eliminate code duplication: unify `start_issue.py` with `run_claude_skill`, extract `_run_gh` helper in `github.py`, consolidate command construction in `claude_runner.py` (#115)

### Removed

- Dead code: `TypeVar T` and `print_warning` from `ui.py`, `get_remote_url` and `create_or_checkout_branch` from `git.py`, `extract_issue_number_from_branch` and `create_branch_from_issue` from `branch.py`, `get_all_command` from `quality_gate.py`, `cwd_for_merge` from `workflow_context.py` (#114)

## [0.2.0] - 2026-02-18

### Added

- `/commit-push-pr` command — bundled commit, push, and PR creation
- `/respond-review` command — respond to hachimoku JSONL review findings
- Agents template system (`git-committer`, `pr-creator`, `pr-merger`, `branch-cleaner`)
- Automatic hachimoku installation and initialization in `issue-workflow init`
- Agents update support in `issue-workflow update`
- `ReviewResult` data model with JSONL parsing, severity classification, and multi-agent support
- `ReviewLoader` service for reading `.hachimoku/reviews/pr-{number}.jsonl`
- Default branch auto-detection via `git symbolic-ref` and `gh api`
- Docker development environment (`docker-compose.yml`, `Makefile`)
- Version consistency tests (`test_version.py`)
- Workflow subcommands via `claude -p` (`start-issue`, `create-pr`, `review-pr`, `push-changes`, `respond-comments`, `merge-pr`, `run`)
- `--force` flag for `/start-issue` to skip TDD confirmations in non-interactive mode
- `.gitignore` management service in `issue-workflow init`
- Real-time 8moku output streaming in `review-pr` subcommand
- Hachimoku version upgrade hint in `issue-workflow update`
- `.hachimoku/` configuration copy to new worktrees
- Versioned installation instructions in README

### Changed

- **BREAKING**: Remove external plugin dependencies (`commit-commands`, `pr-review-toolkit`)
- `/merge-pr` now auto-detects default branch instead of hardcoding `main`
- `__version__` now dynamically read from `pyproject.toml` via `importlib.metadata`
- `UpdateResult` extended with `agents_changes` field
- `scripts/full-workflow.sh` migrated to hachimoku and bundled commands
- Rename "Plugin Commands" section to "Slash Commands" in README
- Git utilities extracted into separate `lib` module
- `complete-issue.sh` renamed to `create-pr.sh`

### Fixed

- `AskUserQuestion` tool disallowed in non-interactive mode
- PR creation incorrectly skipped when merged/closed PRs exist for same branch
- Error suppression patterns replaced with explicit error propagation
- JSON path for assistant event message content in verbose stream
- Null jq output handling in PR creation workflow

### Removed

- `.github/workflows/claude-review.yml` (CI-based external review)
- `WorkflowSettings.ci_review` setting
- `lib_is_ci_review_enabled()` function from `scripts/_lib.sh`
- "Official Plugin Integration" section from README

## [0.1.1] - 2026-01-19

### Added

- DDD (Document-Driven Development) workflow in `/start-issue` Step 4
  - Phase 3 for documentation-first approach before implementation
  - Integration with `doc-updater` skill for documentation updates
  - Support for `documentation.ddd.enabled` and `documentation.ddd.retcon_writing` settings
- Documentation section in `workflow-config.json` schema

### Changed

- Step 4 restructured into 5 phases: Requirements -> Impact Scope -> DDD -> TDD -> Plan
- Output format now includes "Documentation Updates (DDD)" section

## [0.1.0] - 2026-01-15

### Added

- Initial implementation of issue-workflow CLI
- `/start-issue` command for GitHub Issue workflow
- `/init` command with language presets (Python, TypeScript, Go, Rust, Generic)
- TDD workflow support
- Code quality gate integration
- Issue reporter skill
