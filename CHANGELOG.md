# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.1.0] - Initial Release

### Added

- Initial implementation of issue-workflow CLI
- `/start-issue` command for GitHub Issue workflow
- `/init` command with language presets (Python, TypeScript, Go, Rust, Generic)
- TDD workflow support
- Code quality gate integration
- Issue reporter skill
