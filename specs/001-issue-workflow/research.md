# Research: Issue Workflow Toolkit

**Date**: 2026-01-15
**Branch**: `001-issue-workflow`

## 1. CLI実装言語の選定

### Decision: Python 3.13+ (uv + Typer)

### Rationale

1. **既存プロジェクトとの一貫性**
   - CLAUDE.mdでPython専用ルール（uv, ruff, mypy）が明記されている
   - 同一エコシステムでの開発効率が最大化される

2. **CLAUDE.md/Constitution遵守**
   - 型注釈必須（Article 9）→ Typerで型ヒントから自動生成
   - mypy静的型チェック必須 → strictモードで対応
   - Any型禁止 → Pydanticで厳密な型定義

3. **配布の容易さ**
   - `uv tool install issue-workflow` で即座にインストール
   - PyPIで世界中のユーザーにアクセス可能
   - pipx互換で既存のPythonユーザーに親和性高

4. **開発効率**
   - Typerで`--help`、`--non-interactive`が自動生成（FR-003, FR-004）
   - Pydanticで設定ファイルのJSON Schema検証（FR-020）
   - pytest + TDD workflowで品質担保

### Alternatives Considered

| 言語 | 却下理由 |
|------|---------|
| Go | 型システムがCLAUDE.md要件（Any禁止、`| None`構文）と不整合 |
| Rust | cargo installでの初回ビルド時間が長い（15分以上） |
| TypeScript | Node.js依存、既存プロジェクトとの言語分散 |

## 2. CLIフレームワークの選定

### Decision: Typer

### Rationale

1. **型安全性**: Python型ヒントからCLI引数を自動生成
2. **自動ドキュメント**: `--help`が型情報から自動生成
3. **Pydantic統合**: 設定ファイル検証と相性が良い
4. **学習曲線**: Clickの上位互換で既存知識を活用可能

### Alternatives Considered

| フレームワーク | 却下理由 |
|---------------|---------|
| Click | 型ヒント活用が限定的、手動でのhelp記述が必要 |
| argparse | 機能が限定的、コード量が増加 |
| Fire | 型チェックとの相性が悪い |

## 3. 設定ファイル形式

### Decision: JSON with Pydantic validation

### Rationale

1. **JSON Schema対応**: FR-020要件を満たす
2. **Pydantic統合**: 型安全な設定読み込み
3. **エディタ支援**: JSON Schemaでオートコンプリート

### 設定ファイル構造

```json
{
  "$schema": "https://raw.githubusercontent.com/drillan/issue-workflow/main/schemas/workflow-config.schema.json",
  "version": "1.0",
  "language": "python",
  "quality": {
    "lint": "uv run ruff check --fix .",
    "format": "uv run ruff format .",
    "typecheck": "uv run mypy .",
    "test": "uv run pytest",
    "all": "uv run ruff check --fix . && uv run ruff format . && uv run mypy ."
  },
  "workflow": {
    "tdd_required": true,
    "quality_gate_required": true,
    "auto_report": true
  }
}
```

## 4. 言語プリセット設計

### Decision: 5つのプリセット + カスタム対応

### Presets

| プリセット | 品質コマンド | 特徴 |
|-----------|-------------|------|
| Python | ruff, mypy, pytest | uv管理、型チェック重視 |
| TypeScript | eslint, prettier, vitest | npm/pnpm対応 |
| Go | golangci-lint, go test | モジュール対応 |
| Rust | clippy, cargo fmt, cargo test | Cargo統合 |
| Generic | なし（ユーザー定義） | 言語非依存 |

### プリセット設定ファイル

各プリセットは`src/issue_workflow/presets/`にJSONで定義:

```json
{
  "name": "python",
  "display_name": "Python",
  "quality": {
    "lint": "uv run ruff check --fix .",
    "format": "uv run ruff format .",
    "typecheck": "uv run mypy .",
    "test": "uv run pytest",
    "all": "uv run ruff check --fix . && uv run ruff format . && uv run mypy ."
  },
  "files": [
    {
      "path": ".claude/workflow-config.json",
      "template": "workflow-config.json.j2"
    },
    {
      "path": ".claude/git-conventions.md",
      "template": "git-conventions.md"
    }
  ]
}
```

## 5. Plugin配布方式

### Decision: GitHub Repository Fragment

### Rationale

1. **Claude Code標準**: `github:owner/repo#path`形式でPlugin参照
2. **バージョン管理**: タグ指定で特定バージョンを参照可能
3. **自動更新**: リポジトリ更新で即座に反映

### Plugin構造

```
plugin/
├── commands/           # スラッシュコマンド
├── skills/             # バックグラウンドスキル
├── git-conventions.md  # Git規約（FR-022）
└── settings.json       # Plugin設定テンプレート
```

### インストール方式

CLIの`init`コマンドで`.claude/settings.json`に以下を追加:

```json
{
  "plugins": [
    "github:drillan/issue-workflow#plugin"
  ]
}
```

## 6. GitHub CLI連携

### Decision: `gh` CLIをサブプロセスで呼び出し

### Rationale

1. **認証管理**: `gh auth`による既存認証を活用
2. **API安定性**: 公式CLIで安定したAPI提供
3. **依存関係最小化**: Pythonライブラリ不要

### 使用するコマンド

| 操作 | コマンド |
|------|---------|
| Issue取得 | `gh issue view <number> --json number,title,body,labels,state` |
| PR取得 | `gh pr view <number> --json number,title,state,mergeable,headRefName` |
| PRマージ | `gh pr merge <number> --squash --delete-branch` |
| CIチェック | `gh pr checks <number> --watch` |
| コメント投稿 | `gh issue comment <number> --body <body>` |

## 7. ブランチ命名ロジック

### Decision: materials/git-conventions.mdをそのまま採用

### ロジック

1. **ラベルマッピング**: issueラベル → ブランチプレフィックス
2. **キーワード検出**: タイトル・本文からプレフィックス推定
3. **デフォルト**: `feat/`

### 実装

```python
def detect_branch_type(issue: Issue) -> str:
    """issueからブランチタイプを検出する"""
    label_mapping = {
        "enhancement": "feat",
        "feature": "feat",
        "bug": "fix",
        "refactoring": "refactor",
        "refactor": "refactor",
        "documentation": "docs",
        "docs": "docs",
        "test": "test",
        "chore": "chore",
    }

    for label in issue.labels:
        if label.lower() in label_mapping:
            return label_mapping[label.lower()]

    # キーワード検出（フォールバック）
    keywords = {
        "fix": ["bug", "fix", "バグ", "修正", "不具合", "エラー"],
        "refactor": ["refactor", "リファクタ", "整理", "改善"],
        "docs": ["doc", "ドキュメント", "README", "説明"],
        "test": ["test", "テスト"],
        "chore": ["chore", "設定", "config"],
        "feat": ["add", "追加", "新機能", "implement", "実装"],
    }

    text = f"{issue.title} {issue.body}".lower()
    for branch_type, kws in keywords.items():
        if any(kw in text for kw in kws):
            return branch_type

    return "feat"  # デフォルト
```

## 8. 依存関係管理

### Decision: pyproject.toml + uv

### 主要依存関係

```toml
[project]
name = "issue-workflow"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "typer>=0.15.0",
    "pydantic>=2.10.0",
    "rich>=13.9.0",       # プログレス表示
    "readchar>=4.2.0",    # 矢印キー入力（対話的選択UI）
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.14.0",
]

[project.scripts]
issue-workflow = "issue_workflow.cli.main:app"
```

## Summary

| 項目 | 決定 |
|------|------|
| 言語 | Python 3.13+ |
| CLIフレームワーク | Typer |
| 設定形式 | JSON + Pydantic |
| 配布 | PyPI (`uv tool install`) |
| Plugin配布 | `github:drillan/issue-workflow#plugin` |
| GitHub連携 | `gh` CLI |
| テスト | pytest |
| 品質チェック | ruff + mypy |
