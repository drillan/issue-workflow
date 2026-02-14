# CLI Interface Contract

## issue-workflow

メインコマンド。サブコマンドを通じて各機能を提供。

### Global Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--help` | `-h` | flag | ヘルプを表示 |
| `--version` | `-v` | flag | バージョンを表示 |

---

## issue-workflow init

プロジェクトをIssue Workflowで初期化する。

### Synopsis

```
issue-workflow init [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--language` | `-l` | string | (interactive) | 言語プリセット: python, typescript, go, rust, generic |
| `--non-interactive` | | flag | false | 対話モードをスキップ |
| `--force` | `-f` | flag | false | 既存設定を上書き |

### Behavior

1. **対話モード**（`--language`未指定かつ`--non-interactive`なし）:
   - 言語プリセット選択メニューを表示
   - ユーザーが選択後に設定を生成

2. **非対話モード**（`--language`指定または`--non-interactive`あり）:
   - `--language`指定: 指定言語で設定を生成
   - `--non-interactive`のみ: エラー（言語指定必須）

3. **既存設定がある場合**:
   - `--force`あり: 上書き
   - `--force`なし: 確認プロンプト表示（対話モード）またはエラー（非対話モード）

### Output Files

| ファイル / ディレクトリ | 内容 |
|----------|------|
| `.claude/workflow-config.json` | ワークフロー設定 |
| `.claude/git-conventions.md` | Git命名規則 |
| `.claude/commands/` | バンドルコマンド（start-issue, commit-push-pr, merge-pr等） |
| `.claude/agents/` | バンドルエージェント（git-workflow-haiku由来） |
| `.claude/skills/` | バンドルスキル（tdd-workflow, code-quality-gate等） |
| `.hachimoku/` | hachimoku設定（`8moku init`で生成） |

### hachimoku Integration

1. **インストールチェック**: `shutil.which("8moku")`でインストール済みか確認
   - 未インストール: `uv tool install hachimoku`を実行
   - インストール済み: スキップ
2. **プロジェクト初期化チェック**: `.hachimoku/`ディレクトリの存在を確認
   - 未初期化: `8moku init`をサブプロセスとして呼び出し
   - 初期化済み: スキップ

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | 成功 |
| 1 | 一般エラー |
| 2 | 無効な引数 |
| 3 | 既存設定が存在（`--force`なし） |

### Examples

```bash
# 対話モードで初期化
issue-workflow init

# Pythonプリセットで初期化
issue-workflow init -l python

# 非対話モードで初期化（CI環境向け）
issue-workflow init --language python --non-interactive

# 既存設定を上書き
issue-workflow init -l python --force
```

---

## issue-workflow update

設定を更新する（v1.1予定）。

### Synopsis

```
issue-workflow update [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--language` | `-l` | string | (current) | 新しい言語プリセット |
| `--check` | | flag | false | 更新可能かチェックのみ |

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | 成功 |
| 1 | 一般エラー |
| 4 | 設定ファイルが存在しない |

---

## Error Messages

### 共通形式

```
⚠️ {エラーの概要}

{詳細説明}

{解決方法}
```

### エラーカタログ

| エラー | メッセージ |
|--------|----------|
| 言語未指定（非対話モード） | `⚠️ 言語プリセットが必要です\n\n--language オプションで言語を指定してください。\n\n例: issue-workflow init --language python --non-interactive` |
| 無効な言語 | `⚠️ 無効な言語プリセットです: {input}\n\n有効な値: python, typescript, go, rust, generic` |
| 既存設定（force なし） | `⚠️ 設定ファイルが既に存在します\n\n.claude/workflow-config.json が既に存在します。\n上書きするには --force オプションを使用してください。` |
| gh 未インストール | `⚠️ GitHub CLI (gh) が見つかりません\n\nIssue Workflowを使用するにはGitHub CLIが必要です。\n\nインストール: https://cli.github.com/` |
| gh 未認証 | `⚠️ GitHub CLIの認証が必要です\n\n以下のコマンドで認証してください:\n  gh auth login` |
