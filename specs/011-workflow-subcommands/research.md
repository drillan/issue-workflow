# Research: Workflow Subcommands

**Feature Branch**: `011-workflow-subcommands`
**Date**: 2026-02-15

## Research 1: `claude -p` 出力フォーマット

### Decision: 非verbose 時は `--output-format json`、verbose 時は `--output-format stream-json --verbose` を使用

### Rationale

- `--output-format json`（非verbose）は単一 JSON オブジェクトを出力する。`type: "result"` を含み、`result` フィールドにアシスタントの最終テキスト応答が格納される。ログ記録に最適
- `--output-format stream-json` は **`--verbose` が必須**（なしだとエラー）。NDJSON 形式で各イベント（`system/init`, `assistant`, `user/tool_result`, `result`）を1行ずつ出力する
- verbose モードではリアルタイム表示のために `stream-json` を使用し、ログ記録用に最終行（`type: "result"`）を抽出する

### JSON 出力構造（非verbose）

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1393,
  "duration_api_ms": 1281,
  "num_turns": 1,
  "result": "hello",
  "stop_reason": null,
  "session_id": "0baf1b02-...",
  "total_cost_usd": 0.04386575,
  "usage": { ... },
  "modelUsage": { ... },
  "permission_denials": [],
  "uuid": "45b9e716-...",
  "errors": []
}
```

### stream-json イベントタイプ（verbose）

| `type` | `subtype` | 説明 |
|--------|-----------|------|
| `system` | `init` | セッション初期化（cwd, tools, model 等） |
| `assistant` | - | アシスタント応答（text, tool_use） |
| `user` | - | ツール実行結果（tool_result） |
| `result` | `success` / `error_*` | 最終結果 |

### Alternatives Considered

- **JSON配列（`--output-format json --verbose`）**: 全イベントをJSON配列で出力。リアルタイム表示に不向き（全完了まで待つ必要あり）。却下
- **テキスト出力（`--output-format text`）**: 構造化データなし。ログ記録・パースに不向き。却下

---

## Research 2: ログ記録戦略

### Decision: 非verbose/verbose 両方で `result` JSON をログに記録する

### Rationale

- 非verbose: `--output-format json` の出力全体が `result` JSON
- verbose: `stream-json` の最終行（`type: "result"`）を抽出してログに記録
- どちらの場合も同一構造の `result` JSON がログに記録されるため、ログの一貫性を保てる

### ログファイル構造

```
.issue-workflow/logs/YYYY-MM-DD/<command>-<number>-<ISO8601>.jsonl
```

各行は以下のエンベロープ構造:

```json
{"timestamp": "2026-02-15T10:30:00+09:00", "command": "start-issue", "args": {"issue_number": 199}, "exit_code": 0, "result": { ... claude -p の生JSON ... }}
```

### Alternatives Considered

- **ストリーム全体をログに記録**: verbose時の全イベントを記録。ファイルサイズが巨大になる。仕様で「raw JSON を記録するのみ」と明記されているため却下
- **独自フォーマット**: JSON以外の形式。パース困難。却下

---

## Research 3: サブプロセス実行パターン

### Decision: `subprocess.run` を使用（非verbose）、`subprocess.Popen` + 行単位読み取り（verbose）

### Rationale

- 非verbose: `subprocess.run` で同期実行。出力全体をキャプチャし、JSON パースしてログに記録
- verbose: `subprocess.Popen` で起動し、stdout を行単位で読み取りながらリアルタイム表示。最終行（`type: "result"`）を抽出してログに記録
- タイムアウト: `subprocess.run` の `timeout` パラメータ（非verbose）、または `Popen` + タイマー管理（verbose）

### Alternatives Considered

- **`asyncio.create_subprocess_exec`**: 非同期実行。CLIツールでは過剰。複雑性が増す。却下
- **`os.system`**: 出力キャプチャ不可。却下

---

## Research 4: verbose 表示フォーマット

### Decision: Python `json` モジュールで stream-json をパースし、ツール呼び出しを整形表示

### Rationale

- 既存シェルスクリプトでは `jq` を使用していたが、仕様で「Python の json モジュールで処理するため jq は不要」と明記
- `assistant` イベント内の `content` 配列から `tool_use` を抽出し、`● {name}({input_preview}...)` 形式で表示
- `result` イベントでは最終テキスト応答を表示
- Rich Console を使用してカラー出力対応

### 表示フォーマット

```
[start-issue] Starting...
● Bash(git status...)
● Read(/path/to/file...)
● Edit(/path/to/file...)

[start-issue] Done.
```

### Alternatives Considered

- **jq パイプライン**: 外部依存追加。Python ツールキットでjq依存は不適切。仕様で却下済み
- **Rich Live/Progress**: リアルタイム更新UI。`claude -p`のストリーム出力との相性に不確定要素。シンプルな行出力で十分

---

## Research 5: 既存コード再利用分析

### Decision: 以下の既存コンポーネントを直接再利用する

| コンポーネント | ファイル | 再利用する機能 |
|---|---|---|
| `GitOperations` | `lib/git.py` | `get_current_branch()`, `worktree_add/list/remove()`, `get_project_name()` |
| `github.py` | `services/github.py` | `check_gh_availability()`, `get_pr_for_branch()` |
| `worktree.py` | `services/worktree.py` | `copy_hachimoku_to_worktree()`, `find_worktree_for_branch()` |
| `Branch` | `models/branch.py` | `Branch.extract_issue_number()` |
| `ui.py` | `cli/ui.py` | `print_error()`, `print_info()`, `print_success()`, `console` |

### 新規作成が必要なコンポーネント

| コンポーネント | 理由 |
|---|---|
| `ClaudeRunner` | `claude -p` の実行は新機能。既存コードに該当なし |
| `ExecutionLogger` | JSONL ログ記録は新機能 |
| `DependencyChecker` | 外部コマンド確認。既存 `check_gh_availability()` は gh 専用。汎用化が必要 |
| `PR検出サービス` | `get_pr_for_branch` を呼び出すラッパー。ブランチ名取得→PR検索→番号抽出のフローを統合 |

### Alternatives Considered

- **`check_gh_availability` を拡張して他コマンドも対応**: 既存関数は gh 固有のロジック（認証チェック等）を含む。汎用化すると責務が混在する。新規 `DependencyChecker` が適切

---

## Research 6: PR番号検出の実装パターン

### Decision: 引数優先、省略時は `git + gh` で自動検出

### Rationale

- PR番号が引数で指定された場合: そのまま使用（自動検出スキップ）
- PR番号が省略された場合:
  1. `GitOperations.get_current_branch()` で現在のブランチ名を取得
  2. `github.get_pr_for_branch(branch_name)` でPRを検索
  3. `GhResult.data["number"]` からPR番号を抽出
- 検出失敗時: 明確なエラーメッセージ（「先にPRを作成してください」）

### Alternatives Considered

- **`gh pr view --json number`（ブランチ指定なし）**: カレントブランチのPRを自動検出。既存のシェルスクリプトで使用されているが、Pythonサービス層では `get_pr_for_branch` が既に存在し、テスト可能な設計

---

## Research 7: Worktree 操作の実行コンテキスト

### Decision: サブコマンドごとに作業ディレクトリ（cwd）を明示的に制御

### Rationale

仕様により、各サブコマンドの実行コンテキストが異なる:

| サブコマンド | cwd（`--worktree` なし） | cwd（`--worktree` あり） |
|---|---|---|
| `start-issue` | カレントディレクトリ | worktree ディレクトリ |
| `create-pr` | カレントディレクトリ | worktree ディレクトリ |
| `review-pr` | カレントディレクトリ | worktree ディレクトリ |
| `push-changes` | カレントディレクトリ | worktree ディレクトリ |
| `respond-comments` | カレントディレクトリ | worktree ディレクトリ |
| `merge-pr` | カレントディレクトリ | **メインリポジトリ** |
| `run` (各ステップ) | 上記に従う | 上記に従う |

- `ClaudeRunner.run()` は `cwd` パラメータを受け取り、`subprocess.run(cwd=cwd)` で作業ディレクトリを制御する
- `run` サブコマンドは各ステップで適切な cwd を設定する

### Alternatives Considered

- **`os.chdir()` でプロセス全体の cwd を変更**: グローバル状態を変更するため副作用が大きい。テスト困難。却下
