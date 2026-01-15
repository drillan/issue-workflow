# Tasks: Issue Workflow Toolkit

**Input**: Design documents from `/specs/001-issue-workflow/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included (TDD required per CLAUDE.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/issue_workflow/`, `tests/` at repository root
- Plugin files: `plugin/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md (src/issue_workflow/, tests/, plugin/)
- [x] T002 Initialize Python project with pyproject.toml (Python 3.13+, Typer, Pydantic, Rich, readchar)
- [x] T003 [P] Configure ruff and mypy in pyproject.toml
- [x] T004 [P] Create pytest configuration in pyproject.toml and tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create base models: QualityCommands, WorkflowSettings, WorkflowConfig in src/issue_workflow/models/config.py
- [x] T006 [P] Create LanguageName enum and LanguagePreset model in src/issue_workflow/models/preset.py
- [x] T007 [P] Create Issue dataclass in src/issue_workflow/models/issue.py
- [x] T008 [P] Create BranchType enum and Branch dataclass in src/issue_workflow/models/branch.py
- [x] T009 [P] Create MergeStrategy, MergeState, PRState enums and PullRequest dataclass in src/issue_workflow/models/pr.py
- [x] T010 [P] Create Worktree dataclass in src/issue_workflow/models/worktree.py
- [x] T011 Create Git operations helper in src/issue_workflow/lib/git.py
- [x] T012 Create Typer app entry point in src/issue_workflow/cli/main.py
- [x] T013 [P] Create language preset JSON files in src/issue_workflow/presets/ (python.json, typescript.json, go.json, rust.json, generic.json)
- [x] T014 [P] Create git-conventions.md template in src/issue_workflow/templates/git-conventions.md

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Project Initialization (Priority: P1)

**Goal**: Enable developers to initialize Issue Workflow in new or existing projects via CLI

**Independent Test**: Run `issue-workflow init -l python` and verify `.claude/` directory contains configuration files

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T015 [P] [US1] Unit test for config model validation in tests/unit/test_config.py
- [x] T016 [P] [US1] Unit test for preset loading in tests/unit/test_preset.py
- [x] T017 [P] [US1] Integration test for init command in tests/integration/test_init_command.py

### Implementation for User Story 1

- [x] T018 [US1] Implement TemplateService for generating config files in src/issue_workflow/services/template.py
- [x] T019 [US1] Implement preset loader (load JSON, merge with defaults) in src/issue_workflow/services/preset_loader.py
- [x] T020 [US1] Implement interactive language selection UI (Rich + readchar) in src/issue_workflow/cli/ui.py
- [x] T021 [US1] Implement init command with options (--language, --non-interactive, --force) in src/issue_workflow/cli/commands/init.py
- [x] T022 [US1] Add User scope Plugin check (skip if already installed in ~/.config/claude-code/settings.json) in init command
- [x] T023 [US1] Implement gh CLI availability check and error messages in src/issue_workflow/services/github.py

**Checkpoint**: User Story 1 complete - `issue-workflow init` functional

---

## Phase 4: User Story 2 - Start Issue (Priority: P1)

**Goal**: Enable developers to start working on an Issue with automatic branch creation and planning

**Independent Test**: Run `/start-issue 123` with existing GitHub Issue and verify branch creation and plan output

### Tests for User Story 2

- [x] T024 [P] [US2] Unit test for branch type detection from labels/keywords in tests/unit/test_branch.py
- [x] T025 [P] [US2] Unit test for Issue model parsing in tests/unit/test_issue.py
- [x] T026 [P] [US2] Integration test for GitHub service in tests/integration/test_github_service.py

### Implementation for User Story 2

- [x] T027 [US2] Implement `gh issue view` wrapper in src/issue_workflow/services/github.py
- [x] T028 [US2] Implement branch type detection from Issue labels and keywords in src/issue_workflow/services/branch.py
- [x] T029 [US2] Implement branch name normalization (kebab-case, 40-char limit) in src/issue_workflow/services/branch.py
- [x] T030 [US2] Implement branch creation/checkout in src/issue_workflow/lib/git.py
- [x] T031 [US2] Create /start-issue command skill in plugin/commands/start-issue.md

**Checkpoint**: User Story 2 complete - `/start-issue` functional

---

## Phase 5: User Story 3 - TDD Workflow (Priority: P2)

**Goal**: Enforce Red-Green-Refactor cycle during implementation

**Independent Test**: Start implementing a feature and verify TDD skill enforces test-first approach with user approval

### Tests for User Story 3

- [x] T032 [P] [US3] Test file mapping validation (src/*.py → tests/test_*.py) in tests/unit/test_tdd_mapping.py

### Implementation for User Story 3

- [x] T033 [US3] Create tdd-workflow skill definition in plugin/skills/tdd-workflow/SKILL.md

**Checkpoint**: User Story 3 complete - TDD workflow enforced

---

## Phase 6: User Story 4 - Code Quality Gate (Priority: P2)

**Goal**: Automatically run quality checks before commits

**Independent Test**: Attempt to commit and verify quality checks run and block if failures exist

### Tests for User Story 4

- [x] T034 [P] [US4] Test quality command loading from config in tests/unit/test_quality_gate.py

### Implementation for User Story 4

- [x] T035 [US4] Create code-quality-gate skill definition in plugin/skills/code-quality-gate/SKILL.md

**Checkpoint**: User Story 4 complete - Quality gate enforced

---

## Phase 7: User Story 5 - PR Merge and Cleanup (Priority: P2)

**Goal**: Automate PR merge with CI wait and cleanup

**Independent Test**: Run `/merge-pr 100` on a mergeable PR and verify merge completion and cleanup

### Tests for User Story 5

- [x] T036 [P] [US5] Unit test for PullRequest model in tests/unit/test_pr.py
- [x] T037 [P] [US5] Integration test for PR merge operations in tests/integration/test_merge_pr.py

### Implementation for User Story 5

- [x] T038 [US5] Implement `gh pr view` wrapper in src/issue_workflow/services/github.py
- [x] T039 [US5] Implement `gh pr checks --watch` wrapper in src/issue_workflow/services/github.py
- [x] T040 [US5] Implement `gh pr merge` with strategy options in src/issue_workflow/services/github.py
- [x] T041 [US5] Implement worktree detection and cleanup in src/issue_workflow/services/worktree.py
- [x] T042 [US5] Create /merge-pr command skill in plugin/commands/merge-pr.md

**Checkpoint**: User Story 5 complete - `/merge-pr` functional

---

## Phase 8: User Story 6 - Worktree Parallel Work (Priority: P3)

**Goal**: Enable working on multiple Issues in parallel via worktrees

**Independent Test**: Run `/add-worktree 200` and verify new worktree directory is created

### Tests for User Story 6

- [x] T043 [P] [US6] Unit test for Worktree naming in tests/unit/test_worktree.py

### Implementation for User Story 6

- [x] T044 [US6] Implement worktree name generation (project-name-branch format) in src/issue_workflow/models/worktree.py
- [x] T045 [US6] Implement `git worktree add -b` wrapper in src/issue_workflow/lib/git.py
- [x] T046 [US6] Create /add-worktree command skill in plugin/commands/add-worktree.md

**Checkpoint**: User Story 6 complete - `/add-worktree` functional

---

## Phase 9: User Story 7 - Review PR Comments (Priority: P3)

**Goal**: Efficiently review and respond to PR comments

**Independent Test**: Run `/review-pr-comments 300` and verify comment list with action options

### Tests for User Story 7

- [x] T047 [P] [US7] Integration test for PR comment fetching in tests/integration/test_review_comments.py

### Implementation for User Story 7

- [x] T048 [US7] Implement `gh api` wrapper for PR comments in src/issue_workflow/services/github.py
- [x] T049 [US7] Implement PR number detection from current branch in src/issue_workflow/services/github.py
- [x] T050 [US7] Create /review-pr-comments command skill in plugin/commands/review-pr-comments.md

**Checkpoint**: User Story 7 complete - `/review-pr-comments` functional

---

## Phase 10: User Story 8 - Progress Reporting (Priority: P3)

**Goal**: Automatically report progress to GitHub Issues

**Independent Test**: Complete a plan and verify issue-reporter posts comment to Issue

### Tests for User Story 8

- [x] T051 [P] [US8] Unit test for branch-to-issue parsing in tests/unit/test_issue_reporter.py

### Implementation for User Story 8

- [x] T052 [US8] Implement Issue number extraction from branch name in src/issue_workflow/services/branch.py
- [x] T053 [US8] Implement `gh issue comment` wrapper in src/issue_workflow/services/github.py
- [x] T054 [US8] Create issue-reporter skill definition in plugin/skills/issue-reporter/SKILL.md
- [x] T055 [US8] Create doc-updater skill definition in plugin/skills/doc-updater/SKILL.md

**Checkpoint**: User Story 8 complete - Automatic progress reporting functional

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T056 [P] Create plugin settings.json template in plugin/settings.json
- [x] T057 [P] Copy git-conventions.md to plugin/git-conventions.md (implemented as template in src/)
- [x] T058 [P] Add models __init__.py with all exports in src/issue_workflow/models/__init__.py
- [x] T059 [P] Add services __init__.py with all exports in src/issue_workflow/services/__init__.py
- [x] T060 [P] Add lib __init__.py with all exports in src/issue_workflow/lib/__init__.py
- [x] T061 [P] Add cli __init__.py and commands __init__.py in src/issue_workflow/cli/
- [x] T062 [P] Add root __init__.py with version in src/issue_workflow/__init__.py
- [x] T063 Run full quality check: ruff check --fix . && ruff format . && mypy .
- [x] T064 Run all tests: uv run pytest (130 passed)
- [x] T065 Validate quickstart.md scenarios manually (structure validated)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) should complete first
  - US3-5 (P2) can follow
  - US6-8 (P3) can be last
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Init)**: Foundation only - core entry point
- **US2 (Start Issue)**: Foundation + US1 (needs config)
- **US3 (TDD)**: Foundation only - skill definition
- **US4 (Quality Gate)**: Foundation only - skill definition
- **US5 (Merge PR)**: Foundation + US2 (needs github service)
- **US6 (Worktree)**: Foundation + US2 (needs branch service)
- **US7 (Review Comments)**: Foundation + US5 (needs PR service)
- **US8 (Reporter)**: Foundation + US2 (needs branch parsing)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before CLI commands/skills
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (T006-T010, T013-T014)
- All test tasks within a user story marked [P] can run in parallel
- Different user stories with same priority can be worked on in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for config model validation in tests/unit/test_config.py"
Task: "Unit test for preset loading in tests/unit/test_preset.py"
Task: "Integration test for init command in tests/integration/test_init_command.py"
```

## Parallel Example: Foundational Phase

```bash
# Launch all independent model tasks:
Task: "Create LanguageName enum and LanguagePreset model in src/issue_workflow/models/preset.py"
Task: "Create Issue dataclass in src/issue_workflow/models/issue.py"
Task: "Create BranchType enum and Branch dataclass in src/issue_workflow/models/branch.py"
Task: "Create MergeStrategy, MergeState, PRState enums and PullRequest dataclass in src/issue_workflow/models/pr.py"
Task: "Create Worktree dataclass in src/issue_workflow/models/worktree.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Init command)
4. Complete Phase 4: User Story 2 (Start Issue)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Init) → Test → MVP Demo (can initialize projects)
3. Add US2 (Start Issue) → Test → Core workflow functional
4. Add US3-5 (TDD, Quality, Merge) → Test → Full development cycle
5. Add US6-8 (Worktree, Review, Report) → Test → Advanced features
6. Polish → Release v1.0

### Priority Execution Order

| Priority | User Stories | Description |
|----------|--------------|-------------|
| P1 | US1, US2 | Core workflow (Init + Start Issue) |
| P2 | US3, US4, US5 | Quality enforcement (TDD, Quality Gate, Merge) |
| P3 | US6, US7, US8 | Advanced features (Worktree, Review, Reporter) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Quality check required before every commit per CLAUDE.md
