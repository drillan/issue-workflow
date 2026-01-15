# Tasks: Update Command

**Input**: Design documents from `/specs/010-update-command/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD必須（CLAUDE.mdにより）。テストはRed確認後に実装。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Single project structure:
- Source: `src/issue_workflow/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Data models and shared types for update command

- [x] T001 [P] Create FileChangeType enum in src/issue_workflow/models/update.py
- [x] T002 [P] Create FileChangeInfo dataclass in src/issue_workflow/models/update.py
- [x] T003 Create UpdateResult dataclass with computed properties in src/issue_workflow/models/update.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: TemplateService拡張 - 差分検出と更新機能の追加

**⚠️ CRITICAL**: User Story実装の前に完了必須

- [x] T004 Add filecmp import and get_file_changes helper function to src/issue_workflow/services/template.py
- [x] T005 Add update_commands method to TemplateService in src/issue_workflow/services/template.py
- [x] T006 Add update_skills method to TemplateService in src/issue_workflow/services/template.py
- [x] T007 [P] Add UI helper functions (print_added, print_updated, print_deleted) to src/issue_workflow/cli/ui.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 基本的な更新操作 (Priority: P1) 🎯 MVP

**Goal**: `issue-workflow update`コマンドで`.claude/commands`と`.claude/skills`を最新版に更新

**Independent Test**: `issue-workflow update`を実行し、ファイルが更新されることを確認

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Unit test for UpdateResult dataclass in tests/unit/test_update.py
- [x] T009 [P] [US1] Unit test for FileChangeType enum in tests/unit/test_update.py
- [x] T010 [P] [US1] Unit test for update_commands method in tests/unit/test_update.py
- [x] T011 [P] [US1] Unit test for update_skills method in tests/unit/test_update.py
- [x] T012 [US1] Integration test for update command execution in tests/integration/test_update_command.py

### Implementation for User Story 1

- [x] T013 [US1] Create update command module in src/issue_workflow/cli/commands/update.py
- [x] T014 [US1] Implement update callback function with error handling in src/issue_workflow/cli/commands/update.py
- [x] T015 [US1] Add _run_update helper function for core logic in src/issue_workflow/cli/commands/update.py
- [x] T016 [US1] Add .claude/ directory existence check with error message in src/issue_workflow/cli/commands/update.py
- [x] T017 [US1] Implement result display logic (added/updated/deleted counts) in src/issue_workflow/cli/commands/update.py
- [x] T018 [US1] Register update command in main.py in src/issue_workflow/cli/main.py

**Checkpoint**: User Story 1 should be fully functional - `issue-workflow update` works

---

## Phase 4: User Story 2 - 更新前の差分確認 (Priority: P2)

**Goal**: `--dry-run`オプションで実際の更新なしに差分を表示

**Independent Test**: `issue-workflow update --dry-run`を実行し、ファイル変更なしで差分表示されることを確認

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T019 [P] [US2] Unit test for dry-run flag in update_commands in tests/unit/test_update.py
- [x] T020 [P] [US2] Unit test for dry-run flag in update_skills in tests/unit/test_update.py
- [x] T021 [US2] Integration test for --dry-run option in tests/integration/test_update_command.py

### Implementation for User Story 2

- [x] T022 [US2] Add --dry-run option to update command in src/issue_workflow/cli/commands/update.py
- [x] T023 [US2] Implement dry-run display logic ([DRY-RUN] prefix, "would be" messages) in src/issue_workflow/cli/commands/update.py
- [x] T024 [US2] Ensure no file changes when dry_run=True in src/issue_workflow/services/template.py

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: エッジケース対応とコード品質向上

- [x] T025 [P] Add edge case tests (permission errors, partial failures) in tests/unit/test_update.py
- [x] T026 [P] Add edge case tests (.claude/ not exists) in tests/integration/test_update_command.py
- [x] T027 Run ruff check --fix . && ruff format . && mypy .
- [x] T028 Run quickstart.md validation (manual verification of examples)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion, can parallel with US1
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core update functionality
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Adds --dry-run option

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before CLI commands
- CLI commands before registration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 and US2 tests can start in parallel
- All tests for a user story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for UpdateResult dataclass in tests/unit/test_update.py"
Task: "Unit test for FileChangeType enum in tests/unit/test_update.py"
Task: "Unit test for update_commands method in tests/unit/test_update.py"
Task: "Unit test for update_skills method in tests/unit/test_update.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007)
3. Complete Phase 3: User Story 1 (T008-T018)
4. **STOP and VALIDATE**: Test `issue-workflow update` independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP!
3. Add User Story 2 → Test independently → Full feature
4. Polish phase → Production ready

### File Summary

| File Path | Tasks |
|-----------|-------|
| src/issue_workflow/models/update.py | T001, T002, T003 |
| src/issue_workflow/services/template.py | T004, T005, T006, T024 |
| src/issue_workflow/cli/ui.py | T007 |
| src/issue_workflow/cli/commands/update.py | T013, T014, T015, T016, T017, T022, T023 |
| src/issue_workflow/cli/main.py | T018 |
| tests/unit/test_update.py | T008, T009, T010, T011, T019, T020, T025 |
| tests/integration/test_update_command.py | T012, T021, T026 |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
