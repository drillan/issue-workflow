# Quickstart: Issue Workflow Toolkit

## Prerequisites

1. **GitHub CLI** (`gh`) がインストールされ、認証済みであること
   ```bash
   gh auth status
   ```

2. **Python 3.13+** と **uv** がインストールされていること
   ```bash
   python3 --version
   uv --version
   ```

3. プロジェクトが **Gitリポジトリ** として初期化されていること
   ```bash
   git status
   ```

## Installation

```bash
# uvでインストール（推奨）
uv tool install issue-workflow

# または pipx
pipx install issue-workflow
```

## Setup

### Step 1: プロジェクトを初期化

```bash
cd your-project
issue-workflow init -l python
```

以下が生成されます:
- `.claude/workflow-config.json` - ワークフロー設定
- `.claude/git-conventions.md` - Git命名規則
- `.claude/commands/` - スラッシュコマンド（start-issue, commit-push-pr, merge-pr等）
- `.claude/agents/` - エージェント定義（git-workflow-haiku由来）
- `.claude/skills/` - バックグラウンドスキル
- `.hachimoku/` - hachimoku設定（自動インストール + 初期化）

### Step 2: Claude Codeを起動

```bash
claude
```

バンドルされたコマンド・スキルが自動的に読み込まれます。

## Basic Workflow

### 1. Issue作業を開始

```
/start-issue 123
```

このコマンドは:
1. Issue #123 の情報を取得
2. 適切なブランチを作成（例: `feat/123-add-feature`）
3. 実装計画を立案
4. 計画をIssueにコメント

### 2. TDD駆動で実装

tdd-workflowスキルが自動的にTDDサイクルを強制します:

1. **Red**: テストを作成し、失敗を確認
2. **Green**: テストを通過する最小限の実装
3. **Refactor**: コードを改善

### 3. 品質チェック

code-quality-gateスキルがコミット前に自動チェック:

```bash
# 手動で実行する場合
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```

### 4. コミット・プッシュ・PR作成

```
/commit-push-pr
```

このコマンドは:
1. 変更をコミット（メッセージ自動生成）
2. リモートにプッシュ
3. PRを作成

### 5. PRレビュー

hachimoku CLIでPRレビューを実行:

```bash
8moku 300
```

レビュー結果は`.hachimoku/reviews/pr-300.jsonl`に出力されます。

### 6. レビュー指摘への対応

```
/respond-review 300
```

hachimokuのJSONLレビュー結果を読み取り、各指摘への対応方針を決定・実行します。
引数なしの場合は現在のブランチから自動検出:

```
/respond-review
```

### 7. PRをマージ

```
/merge-pr 100
```

このコマンドは:
1. CIチェックの完了を待機
2. squashマージを実行
3. ブランチを削除
4. worktreeを削除（該当する場合）

## Advanced Usage

### ワークツリーで並行作業

複数のIssueを同時に作業する場合:

```
/add-worktree 200
```

新しいワークツリーが作成されます:
```
../your-project-feat-200-add-feature/
```

### レビューコメント対応（人間レビューア）

GitHub上のレビューコメント（人間レビューア等）に対応:

```
/review-pr-comments 100
```

または現在のブランチに紐づくPRの場合:

```
/review-pr-comments
```

## Configuration

### workflow-config.json

```json
{
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

### Language Presets

| プリセット | 説明 |
|-----------|------|
| `python` | Python + uv + ruff + mypy |
| `typescript` | TypeScript + npm + eslint |
| `go` | Go + golangci-lint |
| `rust` | Rust + clippy + cargo |
| `generic` | カスタム設定（ユーザー定義） |

## Troubleshooting

### gh CLIの認証エラー

```
⚠️ GitHub CLIの認証が必要です

gh auth login
```

### 既存設定の上書き

```bash
issue-workflow init -l python --force
```

### hachimokuのインストールエラー

```bash
# 手動インストール
uv tool install hachimoku

# 初期化
8moku init
```

### worktreeの手動削除

```bash
git worktree remove ../your-project-feat-123-xxx
git worktree prune
```
