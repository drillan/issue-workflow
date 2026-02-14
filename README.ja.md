# Issue Workflow Toolkit

[English](README.md) | 日本語

GitHub Issue駆動開発ワークフローツールキット for Claude Code。Issueの開始からPRのマージまで、開発ワークフロー全体を自動化・効率化します。

## 特徴

- **TDD強制ワークフロー** - Red-Green-Refactorサイクルによるテストファースト開発を強制
- **品質ゲート** - コミット前に自動でlint、format、型チェックを実行
- **進捗自動報告** - GitHub Issueに進捗を自動投稿
- **多言語対応** - Python、TypeScript、Go、Rust、Generic用のプリセットを用意

## システム要件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (パッケージマネージャー)
- [gh CLI](https://cli.github.com/) (GitHub CLI)
- [Claude Code](https://www.anthropic.com/claude-code) CLI

## インストール

```bash
uv tool install git+https://github.com/drillan/issue-workflow.git
```

## クイックスタート

```bash
# 1. プロジェクトにワークフロー設定を初期化
issue-workflow init

# 2. または言語プリセットを指定して初期化
issue-workflow init --language python
```

初期化後、Claude Codeのスラッシュコマンドでワークフローを管理：

```
/start-issue 123      # Issue #123の作業を開始
/review-pr-comments   # PRレビューコメントに対応
/merge-pr 456         # PR #456をマージ
```

## アップデート

新バージョンがリリースされたら、ツールキットを更新しコマンド/スキルを同期：

```bash
# 1. ツールキットを更新
uv tool install git+https://github.com/drillan/issue-workflow.git

# 2. プロジェクトのコマンドとスキルを更新
issue-workflow update
```

`--dry-run`で変更内容をプレビュー：

```bash
issue-workflow update --dry-run
```

## CLIコマンド

| コマンド | 説明 |
|---------|------|
| `issue-workflow init` | プロジェクトにIssue Workflowを初期化 |
| `issue-workflow init --language <lang>` | 言語プリセットを指定して初期化 |
| `issue-workflow init --non-interactive` | 対話プロンプトなしで初期化（CI/CD用） |
| `issue-workflow update` | コマンドとスキルを最新バージョンに更新 |
| `issue-workflow update --dry-run` | 変更内容をプレビュー（実際の変更なし） |
| `issue-workflow --version` | バージョンを表示 |
| `issue-workflow --help` | ヘルプを表示 |

## プラグインコマンド（スラッシュコマンド）

Claude Code内で使用するコマンド。推奨ワークフロー順に記載：

| # | コマンド | 説明 | 引数 |
|---|---------|------|------|
| 1 | `/add-worktree` | Issue用の新規ワークツリーを作成（オプション） | `<issue番号>` |
| 2 | `/start-issue` | Issueを読み込み、ブランチを作成し、実装計画を策定 | `<issue番号>` |
| - | `/commit-push-pr` | コミット、プッシュ、PR作成（公式Plugin） | - |
| - | `/pr-review-toolkit:review-pr` | PRレビュー（公式Plugin） | `<PR番号>` |
| 3 | `/review-pr-comments` | PRレビューコメントを確認・対応 | `[PR番号]`（省略可） |
| 4 | `/merge-pr` | CIチェック完了を待機後、PRをマージ | `<PR番号>` |

### 公式Pluginとの連携

本ツールキットは公式Claude Codeプラグインと連携します：

- **commit-commands** - `/commit-push-pr`を提供し、コミット・プッシュ・PR作成を効率化
- **pr-review-toolkit** - `/pr-review-toolkit:review-pr`を提供し、包括的なPRレビューを実現。[GitHub Action](https://github.com/marketplace/actions/claude-pr-reviewer)としてCI化も可能。

## 自動起動スキル

適切なコンテキストで自動的にトリガーされるスキル：

| # | スキル | 説明 | 起動タイミング |
|---|-------|------|---------------|
| 1 | `tdd-workflow` | TDDワークフロー（Red-Green-Refactorサイクル）を強制 | 実装開始時 |
| 2 | `code-quality-gate` | コミット前に品質チェックを実行 | コミット前（必須通過） |
| 3 | `issue-reporter` | Issueに進捗を投稿 | 計画立案時、問題発覚時 |
| 4 | `doc-updater` | ドキュメント更新が必要な変更を検知 | API変更時（任意） |

## 言語プリセット

品質チェックコマンドが事前設定されたプリセット：

| プリセット | 品質ツール |
|-----------|-----------|
| `python` | ruff, mypy, pytest |
| `typescript` | npm run lint/format/typecheck（通常eslint, prettier, tsc） |
| `go` | golangci-lint, go fmt, go vet |
| `rust` | clippy, rustfmt, cargo check |
| `generic` | カスタマイズ可能 |

## 設定

### ワークフロー設定 (`.claude/workflow-config.json`)

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
  },
  "documentation": {
    "paths": ["README.md", "docs/"],
    "changelog": "CHANGELOG.md",
    "ddd": {
      "enabled": true,
      "retcon_writing": true
    }
  },
  "$schema": "https://raw.githubusercontent.com/drillan/issue-workflow/main/schemas/workflow-config.schema.json"
}
```

### ドキュメント設定

`documentation`セクションはドキュメントパスとDDD（Documentation-Driven Development）ワークフローを設定します：

| フィールド | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| `paths` | `string[]` | `["README.md", "docs/"]` | 管理対象のドキュメントファイル/ディレクトリパス |
| `changelog` | `string` | `"CHANGELOG.md"` | CHANGELOGファイルパス |
| `ddd.enabled` | `boolean` | `true` | DDDワークフローを有効化 |
| `ddd.retcon_writing` | `boolean` | `true` | レトコン記述スタイルを強制（機能が既に存在するかのように記述） |

`issue-workflow init`実行時に、これらの設定を対話的にカスタマイズするか、`--non-interactive`でプリセットデフォルトを使用できます。

### Git規約 (`.claude/git-conventions.md`)

ブランチ命名規則とコミットメッセージ規約を定義：

- ブランチ形式: `<type>/<issue-number>-<description>`
- タイプ: `feat/`, `fix/`, `refactor/`, `docs/`, `test/`, `chore/`
- コミット形式: Conventional Commits

## 開発

### セットアップ

```bash
git clone https://github.com/drillan/issue-workflow.git
cd issue-workflow
uv sync
```

### テスト実行

```bash
uv run pytest
```

### 品質チェック

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```

### Docker開発環境

クリーンで再現可能なテスト環境をDockerで構築できます。

**前提条件:** Docker, Docker Compose, [gh CLI](https://cli.github.com/)（ホスト側）

**イメージのビルド:**

```bash
make docker-build
```

**認証:**

- **GitHub CLI** — ホスト側の `gh auth token` から `GH_TOKEN` が自動注入されます
- **Claude Code** — 初回起動時に `claude` を実行しOAuthログインを完了してください。認証情報はDockerの名前付きボリューム（`claude-auth`）に永続化され、`--rm` でコンテナを削除しても維持されます

**使い方:**

```bash
make docker-dev       # 対話的な開発シェル
make docker-test      # pytest を実行
make docker-quality   # ruff + mypy を実行
```

**Claude Code認証のリセット:**

```bash
docker volume rm issue-workflow_claude-auth
```

## トラブルシューティング

### gh CLI認証エラー

`gh`で認証エラーが発生した場合：

```bash
gh auth login
```

### 既存設定の上書き

既存プロジェクトで設定を再初期化する場合：

```bash
issue-workflow init --force
```

### よくある問題

| 問題 | 解決方法 |
|------|---------|
| `gh: command not found` | [GitHub CLI](https://cli.github.com/)をインストール |
| `uv: command not found` | [uv](https://docs.astral.sh/uv/)をインストール |
| ブランチ作成に失敗 | `git status`で未コミットの変更を確認 |
| Issueへのアクセス拒否 | `gh repo view`でリポジトリアクセスを確認 |

## ライセンス

MIT
