# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-14

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

### Changed

- **BREAKING**: Remove external plugin dependencies (`commit-commands`, `pr-review-toolkit`)
- `/merge-pr` now auto-detects default branch instead of hardcoding `main`
- `__version__` now dynamically read from `pyproject.toml` via `importlib.metadata`
- `UpdateResult` extended with `agents_changes` field
- `scripts/full-workflow.sh` migrated to hachimoku and bundled commands
- Rename "Plugin Commands" section to "Slash Commands" in README

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
