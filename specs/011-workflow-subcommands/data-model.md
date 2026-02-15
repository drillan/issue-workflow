# Data Model: Workflow Subcommands

**Feature Branch**: `011-workflow-subcommands`
**Date**: 2026-02-15

## Entity: ClaudeResult

`claude -p --output-format json` の実行結果を表現するデータモデル。

```python
from pydantic import BaseModel, Field, model_validator


class ClaudeResult(BaseModel, frozen=True):
    """Result from claude -p execution.

    claude -p --output-format json の JSON 出力をパースして構築する。
    model_validate_json(raw_stdout) で安全にパース可能。
    """

    type: str = "result"                          # イベントタイプ（常に "result"）
    subtype: str = ""                             # "success", "error_max_budget_usd" 等
    is_error: bool = False                        # エラーかどうか
    result: str = ""                              # アシスタントの最終テキスト応答
    duration_ms: int = 0                          # 実行時間（ミリ秒）
    duration_api_ms: int = 0                      # API 実行時間（ミリ秒）
    num_turns: int = 0                            # ターン数
    total_cost_usd: float = 0.0                   # API コスト（USD）
    session_id: str = ""                          # セッションID
    uuid: str = ""                                # 実行UUID
    exit_code: int = Field(default=0, exclude=True)  # subprocess 終了コード（JSON外）
    raw_json: str = Field(default="", exclude=True)  # 生の stdout 出力（JSON外）
```

**Validation Rules**:
- `exit_code`: 0 = 成功、非0 = 失敗。`claude -p` の subprocess 終了コードであり、JSON出力には含まれないため `exclude=True`
- `raw_json`: 生の stdout 文字列を保持。`ExecutionLog.result` に `json.loads(raw_json)` の結果を格納するために保持。`exclude=True`
- `result`: JSON内の `"result"` フィールド（テキスト応答）。パース失敗時やタイムアウト時は空文字列
- タイムアウト時は `exit_code=-1`, `is_error=True`, `raw_json='{}'` で構築

**Relationships**:
- `ExecutionLog` が `ClaudeResult.raw_json` を `result` フィールドとして格納

---

## Entity: ExecutionLog

JSONL ログの1行（1実行）を表現するデータモデル。

```python
from datetime import datetime

from pydantic import BaseModel


class ExecutionLog(BaseModel):
    """Single execution log entry for JSONL output."""

    timestamp: datetime     # ISO 8601 形式
    command: str            # サブコマンド名 (e.g., "start-issue")
    args: dict[str, object] # 引数辞書 (e.g., {"issue_number": 199})
    exit_code: int          # claude -p の終了コード
    result: object          # claude -p の生 JSON 出力（パース済みオブジェクト）
```

**Validation Rules**:
- `timestamp`: UTC ではなくローカルタイムゾーン付き ISO 8601
- `command`: サブコマンド名のみ（例: `"start-issue"`, `"create-pr"`）。`"issue-workflow"` プレフィックスは含まない
- `args`: サブコマンドに渡された主要引数。verbose/timeout 等のグローバルオプションは含まない
- `exit_code`: `ClaudeResult.exit_code` と同値
- `result`: `ClaudeResult.raw_json` を `json.loads` でパースしたオブジェクト。パース失敗時はエラー情報を含むオブジェクト

**Relationships**:
- `ExecutionLogger` が `ExecutionLog` をシリアライズして JSONL ファイルに書き込む

---

## Entity: DependencyInfo

外部コマンドの依存情報を表現するデータモデル。

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyInfo:
    """External command dependency information."""

    command: str           # コマンド名 (e.g., "claude", "gh", "8moku")
    install_hint: str      # インストール方法の案内
    check_auth: bool       # 認証チェックが必要か (gh のみ True)
```

**Validation Rules**:
- `command`: 空文字列不可
- `install_hint`: 空文字列不可。URL またはコマンドを含む

**Pre-defined Instances** (名前付き定数):

| 定数名 | command | install_hint |
|--------|---------|--------------|
| `CLAUDE_DEPENDENCY` | `claude` | `https://www.anthropic.com/claude-code` |
| `GH_DEPENDENCY` | `gh` | `https://cli.github.com/` |
| `HACHIMOKU_DEPENDENCY` | `8moku` | `uv tool install hachimoku` |

---

## Service: ClaudeRunner

`claude -p` コマンドをサブプロセスとして実行するサービス。

```python
class ClaudeRunner:
    """Service for executing claude -p as subprocess."""

    def run(
        self,
        prompt: str,
        *,
        cwd: Path | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        verbose: bool = False,
        on_tool_use: Callable[[str, str], None] | None = None,
    ) -> ClaudeResult: ...
```

**State Transitions**: なし（ステートレスサービス）

**Behavior**:
- 非verbose: `subprocess.run(["claude", "-p", prompt, "--dangerously-skip-permissions", "--output-format", "json"], cwd=cwd, timeout=timeout_seconds)`
- verbose: `subprocess.Popen(["claude", "-p", prompt, "--dangerously-skip-permissions", "--output-format", "stream-json", "--verbose"], cwd=cwd)` で起動し、stdout を行単位で読み取り
- verbose 時、`on_tool_use` コールバックでツール呼び出しを通知
- タイムアウト時は `subprocess.TimeoutExpired` をキャッチし、`ClaudeResult(exit_code=-1, is_error=True, ...)` を返す

---

## Service: ExecutionLogger

JSONL ログを書き込むサービス。

```python
class ExecutionLogger:
    """Service for writing JSONL execution logs."""

    def __init__(self, base_dir: Path) -> None:
        """Initialize with base log directory (.issue-workflow/logs/)."""
        ...

    def log(self, entry: ExecutionLog) -> Path:
        """Write log entry and return log file path."""
        ...

    def get_log_path(
        self,
        command: str,
        number: int | None = None,
    ) -> Path:
        """Generate log file path.

        Format: .issue-workflow/logs/YYYY-MM-DD/<command>-<number>-<ISO8601>.jsonl
        """
        ...
```

**Behavior**:
- `get_log_path()`: 日付ディレクトリを作成し、ログファイルパスを生成
  - 番号あり: `start-issue-199-2026-02-15T10-30-00.jsonl`
  - 番号なし: `create-pr-2026-02-15T10-45-00.jsonl`
- `log()`: `ExecutionLog` を JSON シリアライズして1行追加

---

## Service: DependencyChecker

外部コマンドの存在を確認するサービス。

```python
def check_dependencies(dependencies: list[DependencyInfo]) -> None:
    """Check if all required external commands are available.

    Raises:
        SystemExit: If any dependency is missing, with install hints.
    """
    ...
```

**Behavior**:
- `shutil.which(command)` でコマンドの存在を確認
- `check_auth=True` の場合（gh）、`check_gh_availability()` も呼び出す
- 不足コマンドがある場合、インストール案内を含むエラーメッセージを表示して `typer.Exit(code=1)` を送出

---

## Service: PR Detector

PR番号を検出するサービス。

```python
def detect_pr_number(pr_number: int | None = None) -> int:
    """Detect PR number from argument or current branch.

    Args:
        pr_number: Explicitly specified PR number (takes priority).

    Returns:
        Detected PR number.

    Raises:
        typer.Exit: If no PR found and no number specified.
    """
    ...
```

**Behavior**:
1. `pr_number` が指定されている場合: そのまま返す
2. `pr_number` が `None` の場合:
   a. `GitOperations().get_current_branch()` でブランチ名取得
   b. `github.get_pr_for_branch(branch_name)` でPR検索
   c. 見つかった場合: PR番号を返す
   d. 見つからない場合: エラーメッセージを表示して `typer.Exit(code=1)` を送出

---

## Entity: WorkflowContext (run コマンド専用・インメモリ)

`run` サブコマンド内でステップ間のメタデータを伝播するインメモリコンテキスト。
永続化しない。途中再開は個別サブコマンドの手動実行で対応する。

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkflowContext:
    """In-memory context for run command step orchestration.

    Accumulates metadata across steps. Not persisted.
    Recovery from failures uses individual subcommands.
    """

    issue_number: int
    pr_number: int | None = None         # Step 2 (create-pr) 完了後に detect_pr_number() で設定
    worktree_path: Path | None = None    # Step 0 (worktree準備) 完了後に設定
    step_results: list[ClaudeResult] = field(default_factory=list)

    @property
    def has_error(self) -> bool:
        """Check if any step has failed."""
        return any(r.is_error or r.exit_code != 0 for r in self.step_results)

    @property
    def last_result(self) -> ClaudeResult | None:
        """Get the most recent step result."""
        return self.step_results[-1] if self.step_results else None

    @property
    def total_cost_usd(self) -> float:
        """Aggregate API cost across all steps."""
        return sum(r.total_cost_usd for r in self.step_results)

    @property
    def cwd_for_skill(self) -> Path | None:
        """Working directory for skill execution (worktree or None for current)."""
        return self.worktree_path

    @property
    def cwd_for_merge(self) -> Path | None:
        """Working directory for merge (always main repo, i.e. None for current)."""
        return None

    def log_number_for_step(self, command: str) -> int | None:
        """Get the appropriate number for log file naming.

        Returns issue_number for start-issue, pr_number for PR-related commands.
        """
        if command == "start-issue":
            return self.issue_number
        if command in ("review-pr", "respond-comments", "merge-pr"):
            return self.pr_number
        return None
```

**Design Rationale: 永続化しない理由**:
- 個別サブコマンドが再開メカニズムとして機能する（`review-pr`, `merge-pr` 等は PR番号を `gh` から自動検出可能）
- 状態ファイルの整合性管理（古い状態の破棄、実際の Git/GitHub 状態との同期）が複雑性を増す
- 仕様の Out of Scope「サブコマンド間の状態共有」に該当
- Constitution Article 4（Simplicity）に準拠

**Step 間のデータフロー**:

```
Step 0 (worktree): → ctx.worktree_path 設定
Step 1 (start-issue): ctx.issue_number 使用 → ClaudeResult → ctx.step_results に追加
                      → exit_code チェック → 失敗時は即時終了
Step 2 (create-pr): → ClaudeResult → ctx.step_results に追加
                    → exit_code チェック → 成功時に detect_pr_number() → ctx.pr_number 設定
Step 3 (review-pr): ctx.pr_number 使用 → ClaudeResult → ctx.step_results に追加
                    → exit_code チェック
Step 4 (merge-pr): ctx.pr_number 使用, cwd=ctx.cwd_for_merge
                   → ClaudeResult → ctx.step_results に追加
```

---

## Constants

```python
# services/claude_runner.py
DEFAULT_TIMEOUT_SECONDS: int = 3600  # 1 hour

# services/execution_logger.py
LOG_BASE_DIR_NAME: str = ".issue-workflow"
LOG_DIR_NAME: str = "logs"

# services/dependency_checker.py
CLAUDE_INSTALL_URL: str = "https://www.anthropic.com/claude-code"
GH_INSTALL_URL: str = "https://cli.github.com/"
HACHIMOKU_INSTALL_HINT: str = "uv tool install hachimoku"
```

---

## Subcommand → Dependency Mapping

| サブコマンド | 必要な依存 |
|---|---|
| `start-issue` | `claude` |
| `start-issue --worktree` | `claude`, `gh` (Issue取得にghが必要) |
| `create-pr` | `claude` |
| `review-pr` | `claude`, `gh`, `8moku` |
| `review-pr --review-only` | `gh`, `8moku` |
| `review-pr --respond-only` | `claude`, `gh` |
| `push-changes` | `claude` |
| `respond-comments` | `claude`, `gh` |
| `merge-pr` | `claude`, `gh` |
| `run` | `claude`, `gh`, `8moku` |
