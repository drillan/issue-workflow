# Data Model: Issue Workflow Toolkit

**Date**: 2026-01-15
**Branch**: `001-issue-workflow`

## Entities

### 1. WorkflowConfig

プロジェクトのワークフロー設定を管理する。

```python
from pydantic import BaseModel, Field

class QualityCommands(BaseModel):
    """品質チェックコマンド設定"""
    lint: str = Field(description="リンターコマンド")
    format: str = Field(description="フォーマッターコマンド")
    typecheck: str = Field(description="型チェックコマンド")
    test: str = Field(description="テストコマンド")
    all: str = Field(description="全チェック実行コマンド")


class WorkflowSettings(BaseModel):
    """ワークフロー動作設定"""
    tdd_required: bool = Field(default=True, description="TDD強制フラグ")
    quality_gate_required: bool = Field(default=True, description="品質ゲート強制フラグ")
    auto_report: bool = Field(default=True, description="自動進捗報告フラグ")


class WorkflowConfig(BaseModel):
    """プロジェクトのワークフロー設定"""
    version: str = Field(default="1.0", description="設定ファイルバージョン")
    language: LanguageName = Field(description="言語プリセット名")
    quality: QualityCommands = Field(description="品質チェックコマンド")
    workflow: WorkflowSettings = Field(default_factory=WorkflowSettings, description="ワークフロー設定")

    model_config = {
        "json_schema_extra": {
            "$schema": "https://raw.githubusercontent.com/drillan/issue-workflow/main/schemas/workflow-config.schema.json"
        }
    }
```

**Storage**: `.claude/workflow-config.json`

**Validation Rules**:
- `version`: セマンティックバージョン形式（"1.0", "1.1"等）
- `language`: 有効なプリセット名（python, typescript, go, rust, generic）
- `quality.*`: 空文字列不可（genericを除く）

### 2. LanguagePreset

言語別の初期設定テンプレート。

```python
from enum import Enum
from pydantic import BaseModel, Field

class LanguageName(str, Enum):
    """サポートする言語"""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    GENERIC = "generic"


class FileTemplate(BaseModel):
    """生成するファイルのテンプレート定義"""
    path: str = Field(description="生成先パス（.claude/からの相対）")
    template: str = Field(description="テンプレートファイル名")


class LanguagePreset(BaseModel):
    """言語プリセット定義"""
    name: LanguageName = Field(description="プリセット識別子")
    display_name: str = Field(description="表示名")
    quality: QualityCommands = Field(description="デフォルト品質コマンド")
    files: list[FileTemplate] = Field(description="生成するファイル一覧")
```

**Storage**: `src/issue_workflow/presets/*.json`（パッケージ内蔵）

### 3. Issue

GitHub Issueの情報を保持する。

```python
from dataclasses import dataclass
from enum import Enum

class IssueState(str, Enum):
    """Issue状態"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class Issue:
    """GitHub Issue情報"""
    number: int
    title: str
    body: str
    labels: list[str]
    state: IssueState

    @property
    def is_open(self) -> bool:
        return self.state == IssueState.OPEN
```

**Source**: GitHub API（`gh issue view`）

**Validation Rules**:
- `number`: 正の整数
- `state`: "OPEN" または "CLOSED"

### 4. Branch

Gitブランチの情報と命名ロジック。

```python
from dataclasses import dataclass
from enum import Enum

class BranchType(str, Enum):
    """ブランチタイプ"""
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"


@dataclass(frozen=True)
class Branch:
    """Gitブランチ情報"""
    type: BranchType
    issue_number: int
    description: str

    @property
    def name(self) -> str:
        """ブランチ名を生成"""
        return f"{self.type.value}/{self.issue_number}-{self.description}"

    @classmethod
    def from_issue(cls, issue: Issue, branch_type: BranchType) -> "Branch":
        """Issueからブランチを生成"""
        description = cls._normalize_description(issue.title)
        return cls(type=branch_type, issue_number=issue.number, description=description)

    @staticmethod
    def _normalize_description(title: str) -> str:
        """タイトルをブランチ名用に正規化"""
        # 小文字化、特殊文字除去、ハイフン区切り、40文字制限
        ...
```

**Naming Rules** (git-conventions.md準拠):
- Format: `<type>/<issue-number>-<description>`
- Issue番号: ゼロパディングなし
- Description: 英語、kebab-case、2-4語、小文字のみ

### 5. PullRequest

GitHub PRの情報を保持する。

```python
from dataclasses import dataclass
from enum import Enum

class MergeStrategy(str, Enum):
    """マージ戦略"""
    SQUASH = "squash"
    MERGE = "merge"
    REBASE = "rebase"


class MergeState(str, Enum):
    """マージ可能状態"""
    MERGEABLE = "MERGEABLE"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


class PRState(str, Enum):
    """PR状態"""
    OPEN = "OPEN"
    MERGED = "MERGED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class PullRequest:
    """GitHub PR情報"""
    number: int
    title: str
    state: PRState
    mergeable: MergeState
    base_ref_name: str
    head_ref_name: str

    @property
    def can_merge(self) -> bool:
        return self.state == PRState.OPEN and self.mergeable == MergeState.MERGEABLE
```

**Source**: GitHub API（`gh pr view`）

### 6. Worktree

Git worktreeの情報を保持する。

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Worktree:
    """Git worktree情報"""
    path: Path
    branch: Branch
    project_name: str

    @property
    def directory_name(self) -> str:
        """ワークツリーディレクトリ名を生成"""
        # feat/123-xxx → project-name-feat-123-xxx
        branch_part = self.branch.name.replace("/", "-")
        return f"{self.project_name}-{branch_part}"

    @property
    def full_path(self) -> Path:
        """フルパスを取得"""
        return self.path.parent / self.directory_name
```

**Naming Rules** (git-conventions.md準拠):
- 配置場所: メインリポジトリの親ディレクトリ
- Format: `../${PROJECT_NAME}-${BRANCH_NAME}` （`/`を`-`に置換）

### 7. ReviewResult

hachimokuによるレビュー結果を保持する。

```python
from dataclasses import dataclass
from enum import Enum


class ReviewSeverity(str, Enum):
    """レビュー指摘の重要度"""
    CRITICAL = "Critical"
    IMPORTANT = "Important"
    SUGGESTION = "Suggestion"


@dataclass(frozen=True)
class ReviewIssueLocation:
    """レビュー指摘の位置情報"""
    file_path: str
    line_number: int


@dataclass(frozen=True)
class ReviewIssue:
    """レビューの個別指摘"""
    agent_name: str
    severity: ReviewSeverity
    description: str
    location: ReviewIssueLocation | None = None
    suggestion: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class ReviewResult:
    """hachimokuによるレビュー結果"""
    review_mode: str
    commit_hash: str
    branch_name: str
    reviewed_at: str
    issues: list[ReviewIssue]

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def has_critical(self) -> bool:
        return any(i.severity == ReviewSeverity.CRITICAL for i in self.issues)
```

**Source**: `.hachimoku/reviews/pr-{number}.jsonl`（JSONL形式、1行1レビュー結果）

**Validation Rules**:
- `review_mode`: "diff" または "pr"
- `commit_hash`: 40文字のhexadecimal文字列
- `severity`: "Critical", "Important", "Suggestion"のいずれか

## Entity Relationships

```
┌─────────────────┐     ┌─────────────────┐
│ WorkflowConfig  │     │ LanguagePreset  │
│                 │────▶│                 │
│ - language      │     │ - name          │
│ - quality       │     │ - quality       │
│ - workflow      │     │ - files         │
└─────────────────┘     └─────────────────┘
                               │
                               │ generates
                               ▼
                        ┌─────────────────┐
                        │ .claude/        │
                        │ workflow-config │
                        │ git-conventions │
                        └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│     Issue       │────▶│     Branch      │
│                 │     │                 │
│ - number        │     │ - type          │
│ - title         │     │ - issue_number  │
│ - labels        │     │ - description   │
└─────────────────┘     └─────────────────┘
        │                       │
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  PullRequest    │     │   Worktree      │
│                 │     │                 │
│ - number        │     │ - path          │
│ - head_ref_name │────▶│ - branch        │
│ - state         │     │ - project_name  │
└─────────────────┘     └─────────────────┘
        │
        │ reviewed by
        ▼
┌─────────────────┐
│  ReviewResult   │
│                 │
│ - review_mode   │
│ - commit_hash   │
│ - branch_name   │
│ - issues[]      │
└─────────────────┘
```

## State Transitions

### Issue Workflow State

```
[Issue Created]
      │
      ▼
[/start-issue] ──────▶ [Branch Created]
      │                      │
      │                      ▼
      │               [Plan Generated]
      │                      │
      │                      ▼
      │               [TDD Cycle]
      │                   │ │ │
      │                   │ │ └──▶ [Red] ──▶ [Green] ──▶ [Refactor]
      │                   │ │              │
      │                   │ └──────────────┘
      │                   │
      │                   ▼
      │               [Quality Gate]
      │                      │
      │                      ▼
      │               [/commit-push-pr]
      │                      │
      │                      ▼
      │               [PR Created]
      │                      │
      │                      ▼
      │               [8moku review]
      │                      │
      │                      ▼
      │               [/respond-review]
      │                      │
      │                      ▼
      │               [/merge-pr]
      │                      │
      │                      ▼
      │               [CI Check Wait]
      │                      │
      │                      ▼
      │               [Merge Complete]
      │                      │
      │                      ▼
      │               [Cleanup]
      │                      │
      │                      ▼
      └──────────────▶ [Issue Closed]
```

### PR Merge State

```
[PR Open]
    │
    ├── mergeable == CONFLICTING ──▶ [Error: Resolve conflicts]
    │
    ├── mergeable == MERGEABLE
    │       │
    │       ▼
    │   [CI Check]
    │       │
    │       ├── PENDING ──▶ [Wait]
    │       │
    │       ├── FAILURE ──▶ [Error: Fix CI]
    │       │
    │       └── SUCCESS
    │             │
    │             ▼
    │         [Merge]
    │             │
    │             ├── squash (default)
    │             ├── merge
    │             └── rebase
    │
    └── state == MERGED ──▶ [Skip: Already merged]
    └── state == CLOSED ──▶ [Error: PR closed]
```
