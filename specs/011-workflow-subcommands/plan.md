# Implementation Plan: Workflow Subcommands

**Branch**: `011-workflow-subcommands` | **Date**: 2026-02-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-workflow-subcommands/spec.md`

## Summary

シェルスクリプト (`scripts/*.sh`) を Python CLI サブコマンドに変換する。各サブコマンドは `claude -p` を介してスキルを呼び出し、実行結果を JSONL 形式でログに記録する。7つのサブコマンド（start-issue, create-pr, review-pr, push-changes, respond-comments, merge-pr, run）を追加し、既存の CLI・サービス層を拡張する。

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Typer 0.15+, Pydantic 2.10+, Rich 13.9+ (既存依存)
**Storage**: ファイルベース (`.issue-workflow/logs/YYYY-MM-DD/*.jsonl`)
**Testing**: pytest 9+ (`uv run pytest`)
**Target Platform**: Linux/macOS (CLI)
**Project Type**: single (既存の `src/issue_workflow/` 構造を拡張)
**Performance Goals**: N/A（CLIツール、対話時間は `claude -p` の実行時間に依存）
**Constraints**: 外部コマンド依存 (`claude`, `gh`, `8moku`)、`subprocess.run` ベースの実行
**Scale/Scope**: 7サブコマンド、3新規サービス、2新規モデル

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Status | Notes |
|---------|--------|-------|
| Art.1 TDD | ✅ PASS | テスト先行で実装する。1機能=1テストファイル |
| Art.2 Documentation | ✅ PASS | 仕様書（spec.md）確認済み。Clarifications セクションで全質問解決済み |
| Art.3 CLI Design | ✅ PASS | `--help`, `--verbose`, `--timeout`, 非対話モード（`claude -p`）をサポート |
| Art.4 Simplicity | ✅ PASS | 1プロジェクト構造を維持。フレームワーク（Typer）を直接使用 |
| Art.5 Code Quality | ✅ PASS | ruff + mypy 必須。全型注釈付き |
| Art.6 Data Accuracy | ✅ PASS | ハードコード禁止。定数は名前付き定数として定義。タイムアウトは`--timeout`で指定可能（デフォルト値は名前付き定数） |
| Art.7 DRY | ✅ PASS | 既存サービス（GitOperations, github.py, worktree.py）を再利用 |
| Art.8 Refactoring | ✅ PASS | 既存CLIを拡張（新ファイル追加、既存の `main.py` にサブコマンド登録） |
| Art.9 Type Safety | ✅ PASS | 全関数に型注釈。Pydanticモデル使用 |
| Art.10 Docstrings | ✅ PASS | Google-style docstring |
| Art.11 Naming | ✅ PASS | `.claude/git-conventions.md` に準拠 |

## Project Structure

### Documentation (this feature)

```text
specs/011-workflow-subcommands/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contract)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/issue_workflow/
├── cli/
│   ├── main.py                    # [MODIFY] サブコマンド登録追加
│   └── commands/
│       ├── init.py                # [EXISTING]
│       ├── update.py              # [EXISTING]
│       ├── start_issue.py         # [NEW] start-issue サブコマンド
│       ├── create_pr.py           # [NEW] create-pr サブコマンド
│       ├── review_pr.py           # [NEW] review-pr サブコマンド
│       ├── push_changes.py        # [NEW] push-changes サブコマンド
│       ├── respond_comments.py    # [NEW] respond-comments サブコマンド
│       ├── merge_pr.py            # [NEW] merge-pr サブコマンド
│       └── run.py                 # [NEW] run (full-workflow) サブコマンド
├── models/
│   ├── execution_log.py           # [NEW] ExecutionLog Pydanticモデル
│   ├── claude_result.py           # [NEW] ClaudeResult Pydanticモデル
│   └── workflow_context.py        # [NEW] WorkflowContext (run コマンド用インメモリコンテキスト)
├── services/
│   ├── claude_runner.py           # [NEW] claude -p 実行サービス
│   ├── execution_logger.py        # [NEW] JSONL ログ記録サービス
│   ├── dependency_checker.py      # [NEW] 外部コマンド存在確認サービス
│   ├── pr_detector.py             # [NEW] PR番号検出サービス（既存 github.py を活用）
│   ├── github.py                  # [EXISTING] get_pr_for_branch 等を再利用
│   └── worktree.py                # [EXISTING] copy_hachimoku_to_worktree 等を再利用
└── lib/
    └── git.py                     # [EXISTING] worktree操作を再利用

tests/
├── unit/
│   ├── test_claude_runner.py      # [NEW] ClaudeRunner テスト
│   ├── test_execution_logger.py   # [NEW] ExecutionLogger テスト
│   ├── test_dependency_checker.py # [NEW] DependencyChecker テスト
│   ├── test_pr_detector.py        # [NEW] PR検出テスト
│   ├── test_execution_log.py      # [NEW] ExecutionLog モデルテスト
│   ├── test_claude_result.py      # [NEW] ClaudeResult モデルテスト
│   └── test_workflow_context.py   # [NEW] WorkflowContext テスト
└── integration/
    ├── test_start_issue_command.py # [NEW]
    ├── test_create_pr_command.py   # [NEW]
    ├── test_review_pr_command.py   # [NEW]
    ├── test_push_changes_command.py # [NEW]
    ├── test_respond_comments_command.py # [NEW]
    ├── test_merge_pr_command.py    # [NEW]
    └── test_run_command.py         # [NEW]
```

**Structure Decision**: 既存の `src/issue_workflow/` 構造を維持し、`cli/commands/` に新サブコマンド、`models/` に新データモデル、`services/` に新サービスを追加する。単一プロジェクト構成を継続。

## Constitution Check (Post-Design)

*Re-evaluated after Phase 1 design completion.*

| Article | Status | Notes |
|---------|--------|-------|
| Art.1 TDD | ✅ PASS | テスト計画確定: unit 6ファイル + integration 7ファイル。1機能=1テストファイル |
| Art.2 Documentation | ✅ PASS | research.md, data-model.md, contracts/, quickstart.md 生成完了 |
| Art.3 CLI Design | ✅ PASS | CLI contract でサブコマンド仕様を定義。`--help` にセキュリティ注意書きを含む |
| Art.4 Simplicity | ✅ PASS | 単一プロジェクト構造を維持。新規サービス4つは最小限の責務分離 |
| Art.5 Code Quality | ✅ PASS | 全モデル・サービスに型注釈。Pydantic BaseModel 使用 |
| Art.6 Data Accuracy | ✅ PASS | 定数 `DEFAULT_TIMEOUT_SECONDS`, `LOG_BASE_DIR_NAME` 等を名前付き定数として定義 |
| Art.7 DRY | ✅ PASS | 既存 `GitOperations`, `github.py`, `worktree.py`, `ui.py` を再利用。新規コードの重複なし |
| Art.8 Refactoring | ✅ PASS | 既存 `main.py` にサブコマンド登録を追加。V2クラスなし |
| Art.9 Type Safety | ✅ PASS | `ClaudeResult`, `ExecutionLog` は Pydantic BaseModel。`DependencyInfo` は frozen dataclass。`Any` 型未使用 |
| Art.10 Docstrings | ✅ PASS | 全 public クラス・関数に Google-style docstring |
| Art.11 Naming | ✅ PASS | サブコマンド名は既存スクリプト名と一致（setup-issue → start-issue はスキル名に合わせて変更） |

## Generated Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| plan.md | `specs/011-workflow-subcommands/plan.md` | This file |
| research.md | `specs/011-workflow-subcommands/research.md` | Phase 0: 調査結果（7項目） |
| data-model.md | `specs/011-workflow-subcommands/data-model.md` | Phase 1: エンティティ・サービス定義 |
| cli-contract.md | `specs/011-workflow-subcommands/contracts/cli-contract.md` | Phase 1: CLI サブコマンド契約 |
| quickstart.md | `specs/011-workflow-subcommands/quickstart.md` | Phase 1: クイックスタートガイド |

## Complexity Tracking

該当なし。Constitution Check の全項目を違反なくパスしている。
