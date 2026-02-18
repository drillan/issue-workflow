# Tasks: Issue Workflow Toolkit

**Input**: Design documents from `/specs/001-issue-workflow/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included (TDD required per CLAUDE.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

> **⚠️ User Story番号の注意**: Phase 1-11（T001-T065）は初期実装時のUser Story番号を使用しています。Issue #32でspec.mdのUser Storyが再編され、Phase 12以降では新しい番号体系を使用しています。対応表:
>
> | 旧番号 (Phase 1-11) | 内容 | 新番号 (Phase 12+, spec.md準拠) |
> |---------------------|------|--------------------------------|
> | US1 | プロジェクト初期化 | US1（同じ） |
> | US2 | Issue作業の開始 | US2（同じ） |
> | US3 | TDD駆動の実装 | US3（同じ） |
> | US4 | 品質チェックゲート | US4（同じ） |
> | US5 | PRマージとクリーンアップ | US7（再編） |
> | US6 | ワークツリー並行作業 | US8（再編） |
> | US7 | レビューコメント対応 | US10（再編） |
> | US8 | 進捗の自動報告 | US11（再編） |
> | — | コミット・プッシュ・PR | US5（新規） |
> | — | PRレビュー実行 | US6（新規） |
> | — | レビュー指摘への対応 | US9（新規） |

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

### Priority Execution Order (初期実装時の番号体系)

> **注**: 以下は初期実装時のUser Story番号です。Issue #32での新番号はファイル冒頭の対応表を参照してください。

| Priority | User Stories | Description |
|----------|--------------|-------------|
| P1 | US1, US2 | Core workflow (Init + Start Issue) |
| P2 | US3, US4, US5 | Quality enforcement (TDD, Quality Gate, Merge) |
| P3 | US6, US7, US8 | Advanced features (Worktree, Review, Reporter) |

---

# Issue #32: 外部プラグイン依存排除

**Input**: plan.md (Issue #32), spec.md (Session 2026-02-13 Clarifications)
**Branch**: `feat/32-remove-external-plugin-deps`
**Date**: 2026-02-14

**目的**: 外部プラグイン（`commit-commands`, `pr-review-toolkit`）への依存を完全排除し、git-workflow-haikuをバンドル、hachimokuを外部ツールとして統合する。

**Tests**: TDD必須（Constitution Article 1）

---

## Phase 12: Foundational for Issue #32 (Blocking Prerequisites)

**Purpose**: Issue #32の全ユーザーストーリーに先行して完了すべきモデル・ライブラリ変更

**⚠️ CRITICAL**: Issue #32のユーザーストーリー作業はこのPhase完了後に開始

### 12a. Default Branch Auto-Detection (FR-025/FR-026)

- [ ] T066 [P] Write tests for `get_default_branch()` in tests/unit/test_git.py — テスト対象: `git symbolic-ref`で正常取得、`set-head --auto`で自動設定後に取得、両方失敗時にエラー送出
- [ ] T067 Implement `get_default_branch()` in src/issue_workflow/lib/git.py — `git symbolic-ref refs/remotes/origin/HEAD`で自動検出。未設定時は`git remote set-head origin --auto`を試行し再取得。失敗時はエラー（GREEN T066）

### 12b. ReviewResult Model

- [ ] T068 [P] Write tests for ReviewResult, ReviewIssue, ReviewSeverity in tests/unit/test_review.py — テスト対象: 正常生成、optional fields（`location: None`, `suggestion: None`, `category: None`）、`issue_count`/`has_critical`プロパティ、JSONL行パースのシナリオ
- [ ] T069 Implement ReviewResult models in src/issue_workflow/models/review.py — ReviewSeverity(Enum), ReviewIssueLocation(frozen dataclass), ReviewIssue(frozen dataclass, location/suggestion/category optional), ReviewResult(frozen dataclass)（GREEN T068）

### 12c. Config ci_review Removal

- [ ] T070 [P] Update tests for ci_review removal in tests/unit/test_config.py — `ci_review`フィールド参照を削除、WorkflowSettingsのテストを更新
- [ ] T071 Remove `ci_review` field from WorkflowSettings in src/issue_workflow/models/config.py（GREEN T070）

### 12d. UpdateResult agents_changes Extension

- [ ] T072 [P] Update tests for `agents_changes` in tests/unit/test_update.py — `agents_changes`フィールド追加、`added_count`/`updated_count`/`has_changes`プロパティが`agents_changes`を含めて集計することを検証
- [ ] T073 Add `agents_changes` field to UpdateResult in src/issue_workflow/models/update.py — `added_count`/`updated_count`/`has_changes`プロパティも`agents_changes`を含めて更新（GREEN T072）

**Checkpoint**: Foundation ready — Issue #32のユーザーストーリー実装を開始可能

---

## Phase 13: User Story 1 - プロジェクト初期化拡張 (Priority: P1) 🎯 MVP

**Goal**: `issue-workflow init`で`.claude/agents/`のコピーとhachimokuのインストール・初期化が実行される。`issue-workflow update`でagents/の更新もサポートする。

**Independent Test**: `issue-workflow init -l python`を実行し、`.claude/agents/`にエージェントファイルがコピーされ、hachimokuがインストールされることを確認する。

### 13a. TemplateService agents/ Support (TDD)

- [ ] T074 [P] [US1] Write tests for `get_agents_source_dir()` in tests/unit/test_template.py — パスが`src/issue_workflow/agents/`を指すことを検証
- [ ] T075 [P] [US1] Write tests for `copy_agents()` in tests/unit/test_copy_commands_skills.py — 新規コピー、既存スキップ、ソースディレクトリ不在時の`SourceDirectoryNotFoundError`送出を検証（`copy_skills()`テストパターンを踏襲）
- [ ] T076 [P] [US1] Write tests for `update_agents()` in tests/unit/test_update.py — ADDED/UPDATED検出、dry_runモード、エラーハンドリングを検証（`update_skills()`テストパターンを踏襲）
- [ ] T077 [P] [US1] Write tests for `generate_all()` agents inclusion in tests/unit/test_template.py — `generate_all()`の返り値にagentsパスが含まれることを検証
- [ ] T078 [US1] Implement `get_agents_source_dir()`, `copy_agents()`, `update_agents()` in src/issue_workflow/services/template.py — 既存の`copy_commands()`/`update_commands()`パターンを踏襲。`generate_all()`に`self.copy_agents(target_dir)`を追加（GREEN T074-T077）

### 13b. Agents Bundle Content

- [ ] T079 [P] [US1] Create src/issue_workflow/agents/ directory with git-workflow-haiku agent files — git-committer.md, pr-creator.md, pr-merger.md, branch-cleaner.md（git-workflow-haikuから取得し、`main`ハードコードを`git symbolic-ref refs/remotes/origin/HEAD`に置換）

### 13c. New Command Bundle Content

- [ ] T080 [P] [US1] Create src/issue_workflow/commands/commit-push-pr.md — git-workflow-haikuのpr-creatorエージェントを活用するコマンド定義。ベースブランチは`git symbolic-ref refs/remotes/origin/HEAD`で自動検出（FR-025）
- [ ] T081 [P] [US1] Create src/issue_workflow/commands/respond-review.md — hachimoku JSONL読み取り（`.hachimoku/reviews/pr-{number}.jsonl`）、重要度順テーブル表示、Accept/Reject対応方針決定、引数なし時のPR番号自動検出

### 13d. HachimokuService (TDD)

- [ ] T082 [P] [US1] Write tests for `setup_hachimoku()` in tests/unit/test_hachimoku.py — テスト対象: (1)未インストール時のインストール+初期化、(2)インストール済み+`.hachimoku/`未存在時の初期化のみ、(3)インストール済み+初期化済み時のスキップ、(4)インストール失敗時のエラー送出
- [ ] T083 [US1] Implement `setup_hachimoku()` in src/issue_workflow/services/hachimoku.py — installチェック（`shutil.which("8moku")`）とinitチェック（`.hachimoku/`存在）を分離。`subprocess.run`で`uv tool install hachimoku`と`8moku init`を実行（GREEN T082）

### 13e. Init Command Update (TDD)

- [ ] T084 [US1] Update tests for init command in tests/unit/test_init.py and tests/integration/test_init_command.py — hachimokuインストール+初期化ステップの検証、agents/コピーが`generate_all()`に含まれることの検証を追加
- [ ] T085 [US1] Update init command in src/issue_workflow/cli/commands/init.py — `generate_all()`後に`setup_hachimoku(project_dir)`を呼び出し。UIフィードバック追加（GREEN T084）

### 13f. Update Command Update (TDD)

- [ ] T086 [US1] Update tests for update command in tests/integration/test_update_command.py — agents/更新の検証を追加（`update_agents()`結果のUIフィードバック）
- [ ] T087 [US1] Update update command in src/issue_workflow/cli/commands/update.py — `update_agents()`呼び出しを追加。UpdateResult表示に`agents_changes`を含める（GREEN T086）

**Checkpoint**: `issue-workflow init`でagents/コピー＋hachimokuセットアップが動作。`issue-workflow update`でagents/更新が動作。SC-009検証可能。

---

## Phase 14: User Story 5 - コミット・プッシュ・PR作成 (Priority: P2)

**Goal**: 外部プラグイン`commit-commands`を使わずに、バンドルされた`/commit-push-pr`コマンドでコミット・プッシュ・PR作成を実行できる。

**Independent Test**: Claude Codeで`/commit-push-pr`を実行し、コミット・プッシュ・PR作成が外部プラグインなしで完了することを確認する。

- [ ] T088 [US5] Finalize src/issue_workflow/commands/commit-push-pr.md content — T080で作成したファイルの内容を検証・調整。git-workflow-haikuのpr-creatorエージェント参照が正しいことを確認

**Checkpoint**: `/commit-push-pr`がバンドルコマンドとして機能。外部プラグイン不要。

---

## Phase 15: User Story 7 - PRマージとクリーンアップ (Priority: P2)

**Goal**: `/merge-pr`のPost-Merge Cleanupで`main`ハードコードを排除し、デフォルトブランチを自動検出する。

**Independent Test**: デフォルトブランチが`main`以外のリポジトリで`/merge-pr`を実行し、正しいブランチに切り替わることを確認する。

- [ ] T089 [US7] Update src/issue_workflow/commands/merge-pr.md — Step 4 Post-Merge Cleanupの`git checkout main`を`git symbolic-ref refs/remotes/origin/HEAD`によるデフォルトブランチ自動検出+チェックアウトに置換（FR-025）

**Checkpoint**: `/merge-pr`がデフォルトブランチを自動検出して切り替え。

---

## Phase 16: User Story 9 - レビュー指摘への対応 (Priority: P3)

**Goal**: hachimokuのJSONLレビュー結果を読み取り、指摘一覧を表示して対応する`/respond-review`コマンドが機能する。

**Independent Test**: `.hachimoku/reviews/pr-{number}.jsonl`が存在する状態で`/respond-review`を実行し、指摘一覧が表示されることを確認する。

- [ ] T090 [US9] Finalize src/issue_workflow/commands/respond-review.md content — T081で作成したファイルの内容を検証・調整。ReviewResultモデル（T069）のフィールドとJSONLスキーマの整合性を確認

**Checkpoint**: `/respond-review`がhachimoku JSONL出力を読み取り、指摘一覧を表示。

---

## Phase 17: Polish & Cross-Cutting Concerns (Issue #32)

**Purpose**: 複数のユーザーストーリーに影響する更新と最終検証

### 17a. Command FR-025 Verification

- [ ] T091 [P] Review src/issue_workflow/commands/start-issue.md for `main` hardcode — `main`のハードコードがないことを確認。暗黙的な基点ブランチ参照があれば`git symbolic-ref`ベースの説明に更新
- [ ] T092 [P] Review src/issue_workflow/commands/add-worktree.md for `main` hardcode — `main`のハードコードがないことを確認

### 17b. Script Updates

- [ ] T093 [P] Update scripts/full-workflow.sh — Step 3: `/commit-commands:commit-push-pr`→`/commit-push-pr`に変更。Step 4: `/pr-review-toolkit:review-pr`→`8moku <番号>`直接呼び出しに変更。`lib_is_ci_review_enabled`分岐を削除。`/respond-review`ステップを追加
- [ ] T094 [P] Update scripts/_lib.sh — `lib_is_ci_review_enabled()`関数を削除

### 17c. Quality & Validation

- [ ] T095 Run `ruff check --fix . && ruff format . && mypy .` across all changed files — 全エラー解消まで次工程禁止（Constitution Article 5）
- [ ] T096 Validate quickstart.md scenarios — init→start-issue→commit-push-pr→8moku review→respond-review→merge-prの一連のフローが文書と整合していることを確認

---

## Dependencies & Execution Order (Issue #32)

### Phase Dependencies

- **Foundational (Phase 12)**: No dependencies on previous phases — can start immediately. BLOCKS all Issue #32 user stories
- **US1 (Phase 13)**: Depends on Phase 12（models/update.py, lib/git.py）
- **US5 (Phase 14)**: Depends on Phase 13（commit-push-pr.md作成済み）
- **US7 (Phase 15)**: Depends on Phase 12（lib/git.py for symbolic-ref）— US1と並行可能
- **US9 (Phase 16)**: Depends on Phase 12（models/review.py）— US1と並行可能
- **Polish (Phase 17)**: Depends on Phases 13-16 completion

### User Story Dependencies

- **US1 (P1)**: Phase 12完了後に開始 — 他のストーリーに依存なし
- **US5 (P2)**: US1に依存（commit-push-pr.mdがバンドル済みである必要）
- **US7 (P2)**: Phase 12完了後に開始 — US1/US5に独立
- **US9 (P3)**: Phase 12完了後に開始 — US1/US5/US7に独立

### Within Each User Story

- Tests MUST be written and FAIL before implementation（Constitution Article 1）
- Models/lib before services
- Services before CLI commands
- Bundle content after Python infrastructure

### Parallel Opportunities

- Phase 12: T066/T068/T070/T072 are all [P] — different files, can run in parallel
- Phase 13: T074/T075/T076/T077 are all [P] — different test targets
- Phase 13: T079/T080/T081/T082 are all [P] — different files
- Phase 15 (US7) can run in parallel with Phase 13 (US1) after Phase 12 completes
- Phase 16 (US9) can run in parallel with Phase 13 (US1) after Phase 12 completes
- Phase 17: T091/T092/T093/T094 are all [P] — different files

---

## Parallel Example: Phase 12 (Foundational)

```bash
# Launch all RED tests in parallel:
Task: "T066 - Write tests for get_default_branch() in tests/unit/test_git.py"
Task: "T068 - Write tests for ReviewResult in tests/unit/test_review.py"
Task: "T070 - Update tests for ci_review removal in tests/unit/test_config.py"
Task: "T072 - Update tests for agents_changes in tests/unit/test_update.py"

# After RED confirmed, launch GREEN implementations:
Task: "T067 - Implement get_default_branch() in lib/git.py"
Task: "T069 - Implement ReviewResult in models/review.py"
Task: "T071 - Remove ci_review from config.py"
Task: "T073 - Add agents_changes to update.py"
```

## Parallel Example: Phase 13 (US1)

```bash
# Launch all TemplateService tests in parallel:
Task: "T074 - Test get_agents_source_dir()"
Task: "T075 - Test copy_agents()"
Task: "T076 - Test update_agents()"
Task: "T077 - Test generate_all() agents inclusion"

# After RED confirmed, implement:
Task: "T078 - Implement agents support in template.py"

# In parallel with T078, launch bundle content + hachimoku test:
Task: "T079 - Create agents/ bundle files"
Task: "T080 - Create commit-push-pr.md"
Task: "T081 - Create respond-review.md"
Task: "T082 - Test setup_hachimoku()"
```

---

## Implementation Strategy (Issue #32)

### MVP First (User Story 1 Only)

1. Complete Phase 12: Foundational (models + lib)
2. Complete Phase 13: US1 (init/update agents + hachimoku)
3. **STOP and VALIDATE**: `issue-workflow init -l python`でagents/コピー＋hachimoku動作を確認
4. SC-009検証: 外部プラグイン設定が不要であることを確認

### Incremental Delivery

1. Phase 12 → Foundation ready
2. Phase 13 (US1) → init/update動作 → **MVP!**
3. Phase 14 (US5) → `/commit-push-pr`バンドル動作
4. Phase 15 (US7) → `/merge-pr`デフォルトブランチ自動検出
5. Phase 16 (US9) → `/respond-review`hachimoku JSONL対応
6. Phase 17 → スクリプト更新 + 品質検証
7. 各フェーズが前のフェーズを壊さずに価値を追加

### Parallel Team Strategy

With multiple developers:

1. Team completes Phase 12 together（4 TDD pairs）
2. Once Phase 12 is done:
   - Developer A: US1 (Phase 13) — most complex, MVP
   - Developer B: US7 (Phase 15) + US9 (Phase 16) — independent, only needs Phase 12
3. After Phase 13:
   - Developer A: US5 (Phase 14) — depends on US1
   - Developer B: Phase 17 Polish
4. Final: Quality checks + validation

---

## Issue #32 Summary

| Phase | Story | Task Count | Description |
|-------|-------|-----------|-------------|
| Phase 12 | — | 8 | Foundational: models + lib |
| Phase 13 | US1 (P1) | 14 | Init/Update agents + hachimoku 🎯 MVP |
| Phase 14 | US5 (P2) | 1 | commit-push-pr validation |
| Phase 15 | US7 (P2) | 1 | merge-pr FR-025 update |
| Phase 16 | US9 (P3) | 1 | respond-review validation |
| Phase 17 | — | 6 | Polish: scripts, quality, validation |
| **Total** | | **31** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- `ruff check --fix . && ruff format . && mypy .` must pass before commit (Constitution Article 5)
