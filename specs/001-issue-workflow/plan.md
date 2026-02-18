# Implementation Plan: 外部プラグイン依存排除 (Issue #32)

**Branch**: `feat/32-remove-external-plugin-deps` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-issue-workflow/spec.md` (Issue #32 Clarifications)

## Summary

外部プラグイン（`commit-commands`, `pr-review-toolkit`）への依存を完全に排除し、git-workflow-haikuのcommands/agents/をissue-workflowにバンドル、PRレビューはhachimoku CLI（`8moku`）を外部ツールとして統合する。具体的には、TemplateServiceにagents/サポートを追加、initコマンドにhachimokuインストール+初期化を追加、新コマンド（`/commit-push-pr`, `/respond-review`）をバンドル、ワークフロースクリプトから外部プラグイン参照を排除する。

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Typer 0.15+, Pydantic 2.10+, Rich 13.9+, readchar 4.2+, shutil, pathlib, subprocess
**Storage**: ファイルベース（`.claude/workflow-config.json`, `.claude/git-conventions.md`, `.hachimoku/reviews/*.jsonl`）
**Testing**: pytest 8.3+, pytest-cov 6.0+
**Target Platform**: Linux/macOS CLI
**Project Type**: single
**Performance Goals**: N/A（CLIツール）
**Constraints**: 外部プラグインへの依存0（SC-009）
**Scale/Scope**: 個人開発者向けCLIツール

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Status | Notes |
|---------|--------|-------|
| Article 1: Test-First | ✅ PASS | TDD必須。すべての新機能（agents/コピー、hachimokuインストール、default branch検出）にテストファーストで対応 |
| Article 2: Documentation Integrity | ✅ PASS | spec.md更新済み、research.md/data-model.md/contracts/quickstart.md全て更新済み |
| Article 3: CLI & Plugin Design | ✅ PASS | `--help`、`--non-interactive`対応済み。エラーメッセージに解決方法含む |
| Article 4: Simplicity | ✅ PASS | 既存のTemplateServiceパターンを拡張。新規プロジェクト追加なし |
| Article 5: Code Quality | ✅ PASS | ruff + mypy必須。コミット前チェック |
| Article 6: Data Accuracy | ✅ PASS | `main`ハードコード排除（FR-025）。`git symbolic-ref`で自動検出 |
| Article 7: DRY | ✅ PASS | `copy_commands`/`copy_skills`パターンを`copy_agents`に再利用 |
| Article 8: Refactoring | ✅ PASS | 既存TemplateService・initコマンドを直接修正。V2クラス作成なし |
| Article 9: Type Safety | ✅ PASS | 全関数に型注釈。Any禁止 |
| Article 10: Docstrings | ✅ PASS | Google-style docstring |
| Article 11: Naming | ✅ PASS | ブランチ命名規則準拠 |

## Project Structure

### Documentation (this feature)

```text
specs/001-issue-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output (updated: sections 9-11 added)
├── data-model.md        # Phase 1 output (updated: ReviewResult entity added)
├── quickstart.md        # Phase 1 output (updated: Plugin→バンドル+hachimoku)
├── contracts/
│   ├── cli-interface.md # Phase 1 output (updated: hachimoku integration)
│   ├── plugin-commands.md # Phase 1 output (updated: +commit-push-pr, +respond-review)
│   └── plugin-skills.md # No changes needed
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/issue_workflow/
├── cli/
│   ├── commands/
│   │   ├── init.py        # MODIFY: hachimokuインストール+初期化追加
│   │   └── update.py      # MODIFY: agents/更新サポート追加
│   ├── main.py
│   └── ui.py
├── commands/
│   ├── start-issue.md
│   ├── commit-push-pr.md  # NEW: git-workflow-haikuからバンドル
│   ├── merge-pr.md        # MODIFY: mainハードコード排除
│   ├── respond-review.md  # NEW: hachimoku JSONL対応
│   ├── review-pr-comments.md
│   └── add-worktree.md
├── agents/                # NEW: git-workflow-haikuからバンドル
│   ├── git-committer.md
│   ├── pr-creator.md
│   ├── pr-merger.md
│   └── branch-cleaner.md
├── lib/
│   └── git.py             # MODIFY: get_default_branch()追加
├── models/
│   ├── config.py          # MODIFY: ci_review設定削除
│   ├── review.py          # NEW: ReviewResult, ReviewIssue等
│   └── ...
├── services/
│   ├── template.py        # MODIFY: copy_agents(), update_agents(), get_agents_source_dir()追加
│   ├── hachimoku.py       # NEW: hachimokuインストール・初期化サービス
│   └── ...
├── templates/
│   └── git-conventions.md
├── skills/
│   └── ...
└── presets/
    └── ...

tests/
├── test_template.py       # MODIFY: agents/テスト追加
├── test_hachimoku.py      # NEW: hachimokuサービスのテスト
├── test_git.py            # MODIFY: get_default_branch()テスト追加
├── test_review.py         # NEW: ReviewResultモデルのテスト
└── ...

scripts/
└── full-workflow.sh       # MODIFY: 外部プラグイン参照排除
```

**Structure Decision**: 既存の`src/issue_workflow/`構造を維持し、`agents/`ディレクトリと`services/hachimoku.py`を追加。`commands/`と同一階層に`agents/`を配置し、TemplateServiceの既存パターン（`copy_*`/`update_*`）を踏襲。

## Implementation Scope

### 変更対象サマリー

| カテゴリ | ファイル | 変更種別 | 概要 |
|---------|---------|---------|------|
| **サービス** | `services/template.py` | MODIFY | `get_agents_source_dir()`, `copy_agents()`, `update_agents()`, `generate_all()`にagents追加 |
| **サービス** | `services/hachimoku.py` | NEW | `setup_hachimoku(project_dir)` — インストール判定とプロジェクト初期化判定を分離（`.hachimoku/`存在チェック） |
| **ライブラリ** | `lib/git.py` | MODIFY | `get_default_branch()` 追加 |
| **モデル** | `models/review.py` | NEW | `ReviewResult`, `ReviewIssue`, `ReviewSeverity`等 |
| **モデル** | `models/config.py` | MODIFY | `ci_review`設定削除 |
| **モデル** | `models/update.py` | MODIFY | `UpdateResult`に`agents_changes`追加。`added_count`/`updated_count`/`has_changes`プロパティの集計対象にも`agents_changes`を含めること |
| **CLI** | `cli/commands/init.py` | MODIFY | hachimokuインストール+初期化ステップ追加 |
| **CLI** | `cli/commands/update.py` | MODIFY | agents/更新対応 |
| **コマンド** | `commands/commit-push-pr.md` | NEW | git-workflow-haikuバンドル |
| **コマンド** | `commands/respond-review.md` | NEW | hachimoku JSONL対応 |
| **コマンド** | `commands/merge-pr.md` | MODIFY | `main`ハードコード→`git symbolic-ref` |
| **コマンド** | `commands/start-issue.md` | MODIFY | `main`ハードコード→`git symbolic-ref` |
| **エージェント** | `agents/*.md` | NEW | git-workflow-haiku由来（4ファイル） |
| **スクリプト** | `scripts/full-workflow.sh` | MODIFY | 外部プラグイン参照排除 |
| **スクリプト** | `scripts/_lib.sh` | MODIFY | `ci_review`関連関数削除、default branch検出 |

### 依存関係グラフ

```
[lib/git.py: get_default_branch()]
       │
       ├──▶ [commands/merge-pr.md]
       ├──▶ [commands/start-issue.md]
       ├──▶ [commands/commit-push-pr.md] (NEW)
       └──▶ [agents/*.md] (NEW)

[models/review.py] (NEW)
       │
       └──▶ [commands/respond-review.md] (NEW)

[services/template.py: copy_agents/update_agents]
       │
       ├──▶ [cli/commands/init.py]
       └──▶ [cli/commands/update.py]

[services/hachimoku.py] (NEW)
       │
       └──▶ [cli/commands/init.py]

[scripts/_lib.sh: ci_review削除]
       │
       └──▶ [scripts/full-workflow.sh]
```

## Complexity Tracking

> 既存のConstitution Check違反なし。複雑性の正当化は不要。

| 項目 | 判定 | 理由 |
|------|------|------|
| プロジェクト数 | 1（変更なし） | Article 4準拠 |
| 新規サービス | 1（hachimoku.py） | 外部ツール統合の責務分離。TemplateServiceに含めるには責務が異なりすぎる |
| 新規モデル | 1（review.py） | hachimoku JSONL解析用。既存モデルに含まれない新しいドメイン |
