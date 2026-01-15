# Implementation Plan: Issue Workflow Toolkit

**Branch**: `001-issue-workflow` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-issue-workflow/spec.md`

## Summary

GitHub Issue駆動の開発ワークフローをClaude Codeで実現するためのツールキット。
Python (uv + Typer) でCLIを実装し、Claude Code Plugin（Skills形式）でワークフロー自動化を提供する。

主要機能:
- `issue-workflow init`: プロジェクト初期化（5つの言語プリセット対応）
- `/start-issue`: Issue読み込み・ブランチ作成・計画立案
- `/merge-pr`: CI完了待機・マージ・クリーンアップ
- `/add-worktree`: ワークツリー作成による並行作業
- TDD強制、品質ゲート、進捗報告の自動化スキル

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Typer (CLI), Pydantic (設定検証), uv (パッケージ管理)
**Storage**: ファイルベース（`.claude/workflow-config.json`, `.claude/git-conventions.md`）
**Testing**: pytest + pytest-cov
**Target Platform**: Linux, macOS, Windows（クロスプラットフォーム）
**Project Type**: Single project (CLI + Plugin)
**Performance Goals**: 初期化5分以内、Issue作業開始2分以内
**Constraints**: GitHub CLI (`gh`) 必須、ネットワーク接続必須
**Scale/Scope**: 個人〜中規模チーム向け

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Requirement | Status | Notes |
|---------|-------------|--------|-------|
| Article 1: Test-First | TDD必須 | PASS | pytest + TDD workflowスキルで強制 |
| Article 2: Documentation | 仕様との整合性 | PASS | spec.mdに基づく実装 |
| Article 3: CLI/Plugin Design | `--help`, `--non-interactive`等 | PASS | Typerで自動対応 |
| Article 4: Simplicity | 最大3プロジェクト | PASS | 単一プロジェクト構成 |
| Article 5: Code Quality | ruff + mypy必須 | PASS | code-quality-gateスキルで強制 |
| Article 6: Data Accuracy | 推測禁止、明示的ソース | PASS | GitHub API/設定ファイルから取得 |
| Article 7: DRY Principle | 重複禁止 | PASS | 共通ロジックをsrc/lib/に集約 |
| Article 8: Refactoring | V2/V3クラス禁止 | N/A | 新規実装 |
| Article 9: Type Safety | 型注釈必須、Any禁止 | PASS | Typer + mypy strictモード |
| Article 10: Docstring | Google-style推奨 | SHOULD | publicモジュールに適用 |
| Article 11: Naming | git-conventions.md準拠 | PASS | materials/git-conventions.mdを採用 |

**Gate Status: PASS** - 全必須要件を満たす設計

## Project Structure

### Documentation (this feature)

```text
specs/001-issue-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI interface定義)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── issue_workflow/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py      # Typer app定義
│   │   ├── main.py          # Entry point
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── init.py      # issue-workflow init
│   │       └── update.py    # issue-workflow update (v1.1予定)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── config.py        # WorkflowConfig (Pydantic)
│   │   ├── issue.py         # Issue dataclass
│   │   └── preset.py        # LanguagePreset enum/config
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github.py        # GitHub API wrapper (gh CLI)
│   │   ├── branch.py        # Branch naming/creation
│   │   └── template.py      # Template generation
│   └── lib/
│       ├── __init__.py
│       └── git.py           # Git operations helper

tests/
├── unit/
│   ├── test_config.py
│   ├── test_preset.py
│   └── test_branch.py
├── integration/
│   ├── test_init_command.py
│   └── test_github_service.py
└── conftest.py              # pytest fixtures

plugin/
├── commands/
│   ├── start-issue.md
│   ├── merge-pr.md
│   ├── add-worktree.md
│   └── review-pr-comments.md
├── skills/
│   ├── tdd-workflow/
│   │   └── SKILL.md
│   ├── code-quality-gate/
│   │   └── SKILL.md
│   ├── issue-reporter/
│   │   └── SKILL.md
│   └── doc-updater/
│   │   └── SKILL.md
├── git-conventions.md
└── settings.json            # Plugin設定テンプレート
```

**Structure Decision**: Single projectを選択。CLI（`src/issue_workflow/`）とPlugin（`plugin/`）を同一リポジトリで管理。Pluginは`github:drillan/issue-workflow#plugin`でインストール可能。

## Complexity Tracking

> 違反なし - 標準的な単一プロジェクト構成で実装可能
