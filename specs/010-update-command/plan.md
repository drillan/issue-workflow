# Implementation Plan: Update Command

**Branch**: `010-update-command` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-update-command/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

`issue-workflow update`コマンドを実装し、ユーザープロジェクトの`.claude/commands`と`.claude/skills`ディレクトリを最新のツールキット内容で更新する。既存の`TemplateService`を拡張し、initコマンドとは異なり「常に上書き」する動作と`--dry-run`オプションによる差分表示機能を提供する。

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Typer 0.15+, Pydantic 2.10+, Rich 13.9+, shutil, pathlib
**Storage**: ファイルシステム（`.claude/commands/`, `.claude/skills/`）
**Testing**: pytest 9.0+ (TDD必須)
**Target Platform**: Linux, macOS, Windows (クロスプラットフォーム対応)
**Project Type**: Single project (既存CLI拡張)
**Performance Goals**: 通常のファイル数（commands 10 + skills 5ディレクトリ）で30秒以内
**Constraints**: ファイルアクセス可能時99%以上の成功率、確認プロンプトなし（CI/CD対応）
**Scale/Scope**: 10ファイル程度のコピー処理

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Requirement | Status | Notes |
|---------|-------------|--------|-------|
| Article 1: Test-First | TDD必須、テスト→承認→Red→実装 | PASS | test_update.pyを先に作成 |
| Article 2: Documentation Integrity | 仕様確認後に実装 | PASS | spec.mdにて明確化済み |
| Article 3: CLI Design | --help, エラーメッセージ, 終了コード | PASS | Typerで標準対応 |
| Article 4: Simplicity | 最小構造、フレームワーク信頼 | PASS | 既存TemplateService活用 |
| Article 5: Code Quality | ruff + mypy必須 | PASS | コミット前チェック |
| Article 6: Data Accuracy | ハードコード禁止 | PASS | パス定数は既存関数使用 |
| Article 7: DRY | 重複禁止 | PASS | TemplateService既存コードを再利用/拡張 |
| Article 8: Refactoring | V2クラス禁止、既存修正 | PASS | TemplateService直接拡張 |
| Article 9: Type Safety | 型注釈必須、Any禁止 | PASS | 全関数に型付け |
| Article 10: Docstrings | Google-style推奨 | PASS | public関数にdocstring |
| Article 11: Naming | 命名規則準拠 | PASS | specs/010-update-command |

**Gate Status**: ALL PASS - Phase 0に進行可能

## Project Structure

### Documentation (this feature)

```text
specs/010-update-command/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - CLIコマンド)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/issue_workflow/
├── cli/
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py          # 既存 - initコマンド
│   │   └── update.py        # NEW - updateコマンド
│   ├── main.py              # 既存 - コマンド登録追加
│   └── ui.py                # 既存 - UI出力関数
├── services/
│   └── template.py          # 既存 - 拡張: force overwrite関数追加
├── commands/                # 更新元 (ツールキット)
└── skills/                  # 更新元 (ツールキット)

tests/
├── unit/
│   └── test_update.py       # NEW - updateコマンドテスト
└── integration/
    └── test_update_command.py  # NEW - E2Eテスト
```

**Structure Decision**: 既存のシングルプロジェクト構造を維持。`cli/commands/update.py`に新コマンドを追加し、`services/template.py`に上書き用メソッドを追加する形で拡張。

## Complexity Tracking

> No constitution violations - complexity tracking not required.
