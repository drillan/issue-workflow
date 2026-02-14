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
   - Pydanticで設定ファイルのJSON Schema検証（FR-027）
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

1. **JSON Schema対応**: FR-027要件を満たす
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

## 5. コンテンツ配布方式

### Decision: CLIバンドル + 外部ツール

### Rationale (Issue #32で更新)

1. **外部プラグイン依存排除**: `commit-commands`, `pr-review-toolkit`への依存をなくし、自作ツールで統一
2. **git-workflow-haikuバンドル**: commands/とagents/をissue-workflowに取り込み、`init`/`update`でコピー
3. **hachimoku外部ツール**: `uv tool install hachimoku`で導入、PRレビュー機能を提供

### バンドル構造

```
src/issue_workflow/templates/
├── commands/           # スラッシュコマンド（start-issue, commit-push-pr, merge-pr等）
├── agents/             # エージェント定義（git-workflow-haiku由来）
├── skills/             # バックグラウンドスキル
└── git-conventions.md  # Git規約（FR-029）
```

### インストール方式

CLIの`init`コマンドで以下を実行:
1. `.claude/commands/`にコマンドファイルをコピー
2. `.claude/agents/`にエージェントファイルをコピー
3. `.claude/skills/`にスキルファイルをコピー
4. `uv tool install hachimoku`でhachimokuをインストール

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

## 9. hachimoku統合方式

### Decision: サブプロセス委譲（Issue #32）

### Rationale

1. **バージョン不整合リスク回避**: `8moku init`のロジックを再実装すると、hachimokuのバージョンアップ時に不整合が発生する
2. **責務の明確な分離**: issue-workflowはインストールとサブプロセス呼び出しのみ担当。hachimokuの内部実装・認証設定はスコープ外
3. **最小限のコード変更**: `subprocess.run(["8moku", "init"])` のみで完結

### 実装方式

```python
def setup_hachimoku(project_dir: Path) -> None:
    """hachimokuをインストールし、プロジェクトを初期化する。"""
    # Step 1: インストール済みチェック（グローバル）
    if shutil.which("8moku") is None:
        # uv tool install で最新版をインストール（バージョン指定なし）
        subprocess.run(["uv", "tool", "install", "hachimoku"], check=True)

    # Step 2: プロジェクト初期化チェック（ローカル）
    hachimoku_dir = project_dir / ".hachimoku"
    if not hachimoku_dir.exists():
        subprocess.run(["8moku", "init"], check=True, cwd=project_dir)
```

### Alternatives Considered

| 方式 | 却下理由 |
|------|---------|
| ロジック吸収（`8moku init`の再実装） | バージョン不整合リスク、保守コスト増大 |
| 手動インストール（ユーザーに委ねる） | SC-001（5分以内の導入完了）を満たせない |

## 10. Default branch自動検出

### Decision: `git symbolic-ref`による自動検出（Issue #32）

### Rationale

1. **FR-025/FR-026準拠**: `main`ハードコード禁止。Gitflow（`develop`）、`master`、その他のブランチ戦略に対応
2. **`git symbolic-ref refs/remotes/origin/HEAD`**: リモートのデフォルトブランチを正確に取得
3. **エッジケース対応**: 未設定時は`git remote set-head origin --auto`で自動設定を試行。失敗時はエラー

### 実装

```python
def get_default_branch() -> str:
    """リモートのデフォルトブランチを取得する。"""
    result = subprocess.run(
        ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        # refs/remotes/origin/main → main
        return result.stdout.strip().removeprefix("refs/remotes/origin/")

    # 未設定の場合、自動設定を試行
    auto_result = subprocess.run(
        ["git", "remote", "set-head", "origin", "--auto"],
        capture_output=True, text=True,
    )
    if auto_result.returncode != 0:
        msg = (
            "デフォルトブランチを検出できません。\n"
            "git remote set-head origin --auto を実行してください。"
        )
        raise RuntimeError(msg)

    # 再取得
    retry = subprocess.run(
        ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
        capture_output=True, text=True, check=True,
    )
    return retry.stdout.strip().removeprefix("refs/remotes/origin/")
```

## 11. 外部プラグイン排除戦略

### Decision: バンドル + hachimoku直接呼び出し（Issue #32）

### 置き換えマッピング

| 旧（外部プラグイン） | 新（Issue #32後） |
|---------------------|-------------------|
| `/commit-commands:commit-push-pr` | `/commit-push-pr`（バンドルコマンド） |
| `/pr-review-toolkit:review-pr` | `8moku review pr <番号>`（直接呼び出し） |
| `ci_review`設定 | 削除（hachimokuに統一） |
| `.claude/settings.json` Plugin設定 | 不要（バンドル方式） |

### ワークフロースクリプト変更

`scripts/full-workflow.sh` の主な変更:
- Step 3: `/commit-commands:commit-push-pr` → `/commit-push-pr`
- Step 4: `/pr-review-toolkit:review-pr` → `8moku review pr`直接呼び出し
- Step 4: `ci_review`モード分岐を削除
- Step 4: `/respond-review`（hachimoku JSONL対応）を追加

## Summary

| 項目 | 決定 |
|------|------|
| 言語 | Python 3.13+ |
| CLIフレームワーク | Typer |
| 設定形式 | JSON + Pydantic |
| 配布 | PyPI (`uv tool install`) |
| コンテンツ配布 | CLIバンドル（commands/ + agents/） + hachimoku外部ツール |
| GitHub連携 | `gh` CLI |
| テスト | pytest |
| 品質チェック | ruff + mypy |
| hachimoku統合 | サブプロセス委譲（`8moku init`呼び出し） |
| Default branch | `git symbolic-ref`による自動検出 |
| 外部プラグイン | 完全排除（バンドル + hachimoku直接呼び出し） |
