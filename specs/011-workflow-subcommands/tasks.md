# Tasks: Workflow Subcommands

**Input**: Design documents from `/specs/011-workflow-subcommands/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Tests**: TDD必須（CLAUDE.md Art.1）。各ユニットテストは実装前に作成し、Red確認後にGreen実装を行う。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/issue_workflow/` (既存構造を拡張)
- **Tests**: `tests/unit/`, `tests/integration/`

---

## Phase 1: Setup

**Purpose**: プロジェクト構造の準備と新規ファイルのスケルトン作成

- [ ] T001 Create new model files with module docstrings in `src/issue_workflow/models/execution_log.py`, `src/issue_workflow/models/claude_result.py`, `src/issue_workflow/models/workflow_context.py`
- [ ] T002 Create new service files with module docstrings in `src/issue_workflow/services/claude_runner.py`, `src/issue_workflow/services/execution_logger.py`, `src/issue_workflow/services/dependency_checker.py`, `src/issue_workflow/services/pr_detector.py`
- [ ] T003 Create new command files with module docstrings in `src/issue_workflow/cli/commands/start_issue.py`, `src/issue_workflow/cli/commands/create_pr.py`, `src/issue_workflow/cli/commands/review_pr.py`, `src/issue_workflow/cli/commands/push_changes.py`, `src/issue_workflow/cli/commands/respond_comments.py`, `src/issue_workflow/cli/commands/merge_pr.py`, `src/issue_workflow/cli/commands/run.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全サブコマンドが依存するモデル・サービスの実装。US8（JSONLログ記録）の基盤を含む

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests (Red first)

- [ ] T004 [P] Write unit tests for ClaudeResult model in `tests/unit/test_claude_result.py` — data-model.md のフィールド定義・バリデーションルールを検証（frozen, model_validate_json, exit_code/raw_json の exclude、タイムアウト時の構築）
- [ ] T005 [P] Write unit tests for ExecutionLog model in `tests/unit/test_execution_log.py` — timestamp/command/args/exit_code/result フィールドの検証、model_dump_json によるシリアライズ
- [ ] T006 [P] Write unit tests for DependencyInfo and DependencyChecker in `tests/unit/test_dependency_checker.py` — shutil.which モック、check_auth=True 時の check_gh_availability 呼び出し、不足時の SystemExit
- [ ] T007 [P] Write unit tests for ClaudeRunner in `tests/unit/test_claude_runner.py` — subprocess.run モック（非verbose）、subprocess.Popen モック（verbose）、タイムアウト時の ClaudeResult 構築、on_tool_use コールバック
- [ ] T008 [P] Write unit tests for ExecutionLogger in `tests/unit/test_execution_logger.py` — get_log_path のファイル名フォーマット（番号あり/なし）、log メソッドによるJSONL書き込み、日付ディレクトリの自動作成
- [ ] T009 [P] Write unit tests for PR detector in `tests/unit/test_pr_detector.py` — 引数優先、省略時の自動検出（GitOperations + github.get_pr_for_branch モック）、未検出時の typer.Exit

### Implementation (Green)

- [ ] T010 [P] Implement ClaudeResult model in `src/issue_workflow/models/claude_result.py` — data-model.md の定義に従い、frozen=True の Pydantic BaseModel、exit_code/raw_json は exclude=True
- [ ] T011 [P] Implement ExecutionLog model in `src/issue_workflow/models/execution_log.py` — data-model.md の定義に従い、Pydantic BaseModel
- [ ] T012 [P] Implement DependencyInfo dataclass and check_dependencies function in `src/issue_workflow/services/dependency_checker.py` — 名前付き定数 CLAUDE_DEPENDENCY, GH_DEPENDENCY, HACHIMOKU_DEPENDENCY を定義
- [ ] T013 Implement ClaudeRunner service in `src/issue_workflow/services/claude_runner.py` — 非verbose: subprocess.run + json output、verbose: subprocess.Popen + stream-json 行読み取り、DEFAULT_TIMEOUT_SECONDS 定数
- [ ] T014 Implement ExecutionLogger service in `src/issue_workflow/services/execution_logger.py` — get_log_path（番号あり/なし）、log メソッド（JSONL書き込み）、LOG_BASE_DIR_NAME/LOG_DIR_NAME 定数
- [ ] T015 Implement detect_pr_number function in `src/issue_workflow/services/pr_detector.py` — 既存 GitOperations.get_current_branch() + github.get_pr_for_branch() を活用

### Test verification

- [ ] T016 Run all foundational unit tests (`uv run pytest tests/unit/test_claude_result.py tests/unit/test_execution_log.py tests/unit/test_dependency_checker.py tests/unit/test_claude_runner.py tests/unit/test_execution_logger.py tests/unit/test_pr_detector.py -v`) and verify all pass

**Checkpoint**: 基盤サービス（ClaudeRunner, ExecutionLogger, DependencyChecker, PR検出）が全て動作。サブコマンド実装に着手可能

---

## Phase 3: User Story 1 - Issue作業開始サブコマンド (Priority: P1) 🎯 MVP

**Goal**: `issue-workflow start-issue <issue-number>` でIssue作業を開始できる。`--worktree` でworktree分離もサポート

**Independent Test**: `issue-workflow start-issue 199` を実行し、claude -p によるstart-issueスキル実行が完了する

### Tests for User Story 1

- [ ] T017 [P] [US1] Write unit test for start-issue command in `tests/unit/test_start_issue_command.py` — 引数パース、worktree有無での分岐、依存チェック呼び出し、ClaudeRunner.run 呼び出し、ExecutionLogger.log 呼び出し
- [ ] T018 [P] [US1] Write integration test for start-issue command in `tests/integration/test_start_issue_command.py` — Typer CLI の CliRunner での E2E テスト（subprocess モック）、verbose/non-verbose、worktree オプション、不正引数のエラー

### Implementation for User Story 1

- [ ] T019 [US1] Implement start-issue subcommand in `src/issue_workflow/cli/commands/start_issue.py` — Typer app 定義、issue_number 引数、--worktree/--verbose/--timeout オプション、依存チェック → worktree準備（任意） → ClaudeRunner.run → ExecutionLogger.log → 終了コード。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` に `--dangerously-skip-permissions` セキュリティ通知を含める（FR-002）
- [ ] T020 [US1] Register start-issue subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T021 [US1] Run US1 tests and verify all pass (`uv run pytest tests/unit/test_start_issue_command.py tests/integration/test_start_issue_command.py -v`)

**Checkpoint**: `issue-workflow start-issue` が動作し、JSONLログが記録される

---

## Phase 4: User Story 2 - PR作成サブコマンド (Priority: P1)

**Goal**: `issue-workflow create-pr` で変更のコミット・プッシュ・PR作成を一連で実行できる

**Independent Test**: 変更がある状態で `issue-workflow create-pr` を実行し、commit-push-prスキルが実行される

### Tests for User Story 2

- [ ] T022 [P] [US2] Write unit test for create-pr command in `tests/unit/test_create_pr_command.py` — 依存チェック、ClaudeRunner.run 呼び出し（プロンプト `/commit-push-pr`）、ログ記録
- [ ] T023 [P] [US2] Write integration test for create-pr command in `tests/integration/test_create_pr_command.py` — CliRunner での E2E テスト、verbose モード

### Implementation for User Story 2

- [ ] T024 [US2] Implement create-pr subcommand in `src/issue_workflow/cli/commands/create_pr.py` — Typer app 定義、引数なし、--verbose/--timeout オプション、依存チェック → ClaudeRunner.run → ExecutionLogger.log。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` にセキュリティ通知を含める（FR-002）
- [ ] T025 [US2] Register create-pr subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T026 [US2] Run US2 tests and verify all pass (`uv run pytest tests/unit/test_create_pr_command.py tests/integration/test_create_pr_command.py -v`)

**Checkpoint**: `issue-workflow create-pr` が動作

---

## Phase 5: User Story 3 - PRレビューサブコマンド (Priority: P2)

**Goal**: `issue-workflow review-pr [pr-number]` でhachimokuレビュー＋レビュー対応を実行できる。--review-only/--respond-only で部分実行も可能

**Independent Test**: PRが存在する状態で `issue-workflow review-pr` を実行し、hachimokuレビューとrespond-reviewスキルが実行される

### Tests for User Story 3

- [ ] T027 [P] [US3] Write unit test for review-pr command in `tests/unit/test_review_pr_command.py` — PR番号検出、--review-only/--respond-only の分岐、相互排他エラー、依存チェック（条件付き）、8moku 実行、ClaudeRunner.run 呼び出し
- [ ] T028 [P] [US3] Write integration test for review-pr command in `tests/integration/test_review_pr_command.py` — CliRunner での E2E テスト、PR番号明示/省略、review-only/respond-only オプション

### Implementation for User Story 3

- [ ] T029 [US3] Implement review-pr subcommand in `src/issue_workflow/cli/commands/review_pr.py` — Typer app 定義、pr_number オプション引数、--review-only/--respond-only/--verbose/--timeout オプション、依存チェック → PR番号検出 → 8moku実行（任意） → ClaudeRunner.run（任意） → ログ記録。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` にセキュリティ通知を含める（FR-002）
- [ ] T030 [US3] Register review-pr subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T031 [US3] Run US3 tests and verify all pass (`uv run pytest tests/unit/test_review_pr_command.py tests/integration/test_review_pr_command.py -v`)

**Checkpoint**: `issue-workflow review-pr` が動作（review-only/respond-only 含む）

---

## Phase 6: User Story 4 - 変更プッシュサブコマンド (Priority: P2)

**Goal**: `issue-workflow push-changes` でレビュー対応後の変更をコミット・プッシュできる（PR作成スキップ）

**Independent Test**: 変更がある状態で `issue-workflow push-changes` を実行し、commit-push-prスキルがPR作成スキップ指示付きで実行される

### Tests for User Story 4

- [ ] T032 [P] [US4] Write unit test for push-changes command in `tests/unit/test_push_changes_command.py` — 依存チェック（`claude` + `gh`）、PR番号自動検出（FR-015a）、ClaudeRunner.run 呼び出し（プロンプトにPR作成スキップ指示を含む）、ログ記録（ログファイル名にPR番号を含む）
- [ ] T033 [P] [US4] Write integration test for push-changes command in `tests/integration/test_push_changes_command.py` — CliRunner での E2E テスト、PR番号自動検出によるログファイル名検証

### Implementation for User Story 4

- [ ] T034 [US4] Implement push-changes subcommand in `src/issue_workflow/cli/commands/push_changes.py` — Typer app 定義、引数なし、--verbose/--timeout オプション、依存チェック（`claude` + `gh`） → PR番号自動検出（FR-015a、ログファイル名に使用） → ClaudeRunner.run → ExecutionLogger.log。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` にセキュリティ通知を含める（FR-002）
- [ ] T035 [US4] Register push-changes subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T036 [US4] Run US4 tests and verify all pass (`uv run pytest tests/unit/test_push_changes_command.py tests/integration/test_push_changes_command.py -v`)

**Checkpoint**: `issue-workflow push-changes` が動作

---

## Phase 7: User Story 5 - レビューコメント対応サブコマンド (Priority: P2)

**Goal**: `issue-workflow respond-comments [pr-number]` でPRのレビューコメントに対応できる

**Independent Test**: レビューコメントのあるPRに対して `issue-workflow respond-comments` を実行し、review-pr-commentsスキルが実行される

### Tests for User Story 5

- [ ] T037 [P] [US5] Write unit test for respond-comments command in `tests/unit/test_respond_comments_command.py` — PR番号検出、依存チェック、ClaudeRunner.run 呼び出し（プロンプト `/review-pr-comments {pr_number}`）
- [ ] T038 [P] [US5] Write integration test for respond-comments command in `tests/integration/test_respond_comments_command.py` — CliRunner での E2E テスト、PR番号明示/省略

### Implementation for User Story 5

- [ ] T039 [US5] Implement respond-comments subcommand in `src/issue_workflow/cli/commands/respond_comments.py` — Typer app 定義、pr_number オプション引数、--verbose/--timeout オプション、依存チェック → PR番号検出 → ClaudeRunner.run → ログ記録。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` にセキュリティ通知を含める（FR-002）
- [ ] T040 [US5] Register respond-comments subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T041 [US5] Run US5 tests and verify all pass (`uv run pytest tests/unit/test_respond_comments_command.py tests/integration/test_respond_comments_command.py -v`)

**Checkpoint**: `issue-workflow respond-comments` が動作

---

## Phase 8: User Story 6 - PRマージサブコマンド (Priority: P2)

**Goal**: `issue-workflow merge-pr [pr-number]` でCI待機・マージ・後処理を実行できる。メインリポジトリから実行する

**Independent Test**: PRが存在する状態で `issue-workflow merge-pr` を実行し、merge-prスキルが実行される

### Tests for User Story 6

- [ ] T042 [P] [US6] Write unit test for merge-pr command in `tests/unit/test_merge_pr_command.py` — PR番号検出、依存チェック、ClaudeRunner.run 呼び出し（プロンプト `/merge-pr {pr_number}`）、cwd=None（メインリポジトリ）
- [ ] T043 [P] [US6] Write integration test for merge-pr command in `tests/integration/test_merge_pr_command.py` — CliRunner での E2E テスト、PR番号明示/省略

### Implementation for User Story 6

- [ ] T044 [US6] Implement merge-pr subcommand in `src/issue_workflow/cli/commands/merge_pr.py` — Typer app 定義、pr_number オプション引数、--verbose/--timeout オプション、依存チェック → PR番号検出 → ClaudeRunner.run → ログ記録。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` にセキュリティ通知を含める（FR-002）
- [ ] T045 [US6] Register merge-pr subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T046 [US6] Run US6 tests and verify all pass (`uv run pytest tests/unit/test_merge_pr_command.py tests/integration/test_merge_pr_command.py -v`)

**Checkpoint**: `issue-workflow merge-pr` が動作

---

## Phase 9: User Story 7 - フルワークフロー実行 (Priority: P2)

**Goal**: `issue-workflow run <issue-number>` で全ステップ（start-issue → create-pr → review+respond+push → merge-pr）を順次自動実行できる

**Independent Test**: `issue-workflow run 199` を実行し、全段階の処理が順次実行される

### Tests for User Story 7

- [ ] T047 [P] [US7] Write unit tests for WorkflowContext in `tests/unit/test_workflow_context.py` — has_error, last_result, total_cost_usd, cwd_for_skill/cwd_for_merge, log_number_for_step のプロパティ検証
- [ ] T048 [P] [US7] Write unit test for run command in `tests/unit/test_run_command.py` — 全ステップの順次実行、途中失敗での即時終了、--worktree でのcwd制御、step_results への結果蓄積
- [ ] T049 [P] [US7] Write integration test for run command in `tests/integration/test_run_command.py` — CliRunner での E2E テスト、全ステップ成功、途中失敗、worktree オプション

### Implementation for User Story 7

- [ ] T050 [US7] Implement WorkflowContext dataclass in `src/issue_workflow/models/workflow_context.py` — data-model.md の定義に従い、step_results, has_error, cwd_for_skill/cwd_for_merge, log_number_for_step
- [ ] T051 [US7] Implement run subcommand in `src/issue_workflow/cli/commands/run.py` — Typer app 定義、issue_number 引数、--worktree/--verbose/--timeout オプション、WorkflowContext を使って順次実行: Step 0（worktree準備、任意）→ Step 1（start-issue）→ Step 2（create-pr）→ Step 3a（8moku review）→ Step 3b（respond-review）→ Step 3c（push-changes）→ Step 4（merge-pr）。各ステップ失敗で即時終了。開始・完了メッセージ表示（cli-contract.md Console Output 参照）。`--help` にセキュリティ通知を含める（FR-002）
- [ ] T052 [US7] Register run subcommand in `src/issue_workflow/cli/main.py` — `_register_commands()` に追加
- [ ] T053 [US7] Run US7 tests and verify all pass (`uv run pytest tests/unit/test_workflow_context.py tests/unit/test_run_command.py tests/integration/test_run_command.py -v`)

**Checkpoint**: `issue-workflow run` が全ステップを順次実行。全7サブコマンドが動作

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: 品質確認と仕上げ

- [ ] T054 Run full test suite (`uv run pytest -v`) and verify all tests pass
- [ ] T055 Run quality checks (`uv run ruff check --fix . && uv run ruff format . && uv run mypy .`) and fix all issues
- [ ] T056 Verify all 7 subcommands show correct `--help` output with security notice (`issue-workflow start-issue --help`, etc.)
- [ ] T057 Run quickstart.md validation — quickstart.md の全コマンド例を `--help` で確認

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2
- **User Story 2 (Phase 4)**: Depends on Phase 2 — can run in parallel with US1
- **User Story 3 (Phase 5)**: Depends on Phase 2 — can run in parallel with US1/US2
- **User Story 4 (Phase 6)**: Depends on Phase 2 — can run in parallel with US1/US2/US3
- **User Story 5 (Phase 7)**: Depends on Phase 2 — can run in parallel with US1-US4
- **User Story 6 (Phase 8)**: Depends on Phase 2 — can run in parallel with US1-US5
- **User Story 7 (Phase 9)**: Depends on Phase 2 AND US1-US6（全サブコマンドをオーケストレーションするため）
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (start-issue, P1)**: Phase 2 完了後に開始可能。他ストーリーに依存しない
- **US2 (create-pr, P1)**: Phase 2 完了後に開始可能。他ストーリーに依存しない
- **US3 (review-pr, P2)**: Phase 2 完了後に開始可能。他ストーリーに依存しない
- **US4 (push-changes, P2)**: Phase 2 完了後に開始可能。他ストーリーに依存しない
- **US5 (respond-comments, P2)**: Phase 2 完了後に開始可能。他ストーリーに依存しない
- **US6 (merge-pr, P2)**: Phase 2 完了後に開始可能。他ストーリーに依存しない
- **US7 (run, P2)**: 全個別サブコマンド（US1-US6）の実装完了後に開始。オーケストレーション層のため

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Implementation follows test verification
- Registration in main.py after implementation
- Test verification run at story completion

### Parallel Opportunities

- Phase 2: T004-T009（全テスト）は並列実行可能。T010-T012 も並列実行可能
- Phase 3-8（US1-US6）: 全て Phase 2 完了後に並列開始可能（異なるファイルを扱うため）
- 各ストーリー内: ユニットテストとインテグレーションテストは並列作成可能

---

## Parallel Example: User Story 1

```bash
# Launch tests for US1 together:
Task: "Write unit test for start-issue in tests/unit/test_start_issue_command.py"
Task: "Write integration test for start-issue in tests/integration/test_start_issue_command.py"

# After tests pass (Red), implement:
Task: "Implement start-issue subcommand in src/issue_workflow/cli/commands/start_issue.py"
```

## Parallel Example: Foundational Phase

```bash
# Launch all foundational tests together:
Task: "Unit tests for ClaudeResult in tests/unit/test_claude_result.py"
Task: "Unit tests for ExecutionLog in tests/unit/test_execution_log.py"
Task: "Unit tests for DependencyChecker in tests/unit/test_dependency_checker.py"
Task: "Unit tests for ClaudeRunner in tests/unit/test_claude_runner.py"
Task: "Unit tests for ExecutionLogger in tests/unit/test_execution_logger.py"
Task: "Unit tests for PR detector in tests/unit/test_pr_detector.py"

# Launch all model implementations together (after tests):
Task: "Implement ClaudeResult in src/issue_workflow/models/claude_result.py"
Task: "Implement ExecutionLog in src/issue_workflow/models/execution_log.py"
Task: "Implement DependencyInfo in src/issue_workflow/services/dependency_checker.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup（スケルトンファイル作成）
2. Complete Phase 2: Foundational（モデル + サービス + テスト）
3. Complete Phase 3: User Story 1（start-issue）
4. Complete Phase 4: User Story 2（create-pr）
5. **STOP and VALIDATE**: start-issue → create-pr のフローをテスト
6. `issue-workflow start-issue 199 && issue-workflow create-pr` が動作することを確認

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US1 (start-issue) + US2 (create-pr) → MVP（Issue開始〜PR作成）
3. US3 (review-pr) + US4 (push-changes) → レビューサイクル
4. US5 (respond-comments) + US6 (merge-pr) → 完全なワークフロー
5. US7 (run) → 全自動実行
6. Polish → 品質確認・仕上げ

### Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD Red-Green)
- Run `uv run ruff check --fix . && uv run ruff format . && uv run mypy .` after each phase
- Stop at any checkpoint to validate story independently
