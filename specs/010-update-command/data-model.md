# Data Model: Update Command

**Date**: 2026-01-15
**Updated**: 2026-02-15
**Feature**: Update Command
**Spec**: [spec.md](./spec.md)

## Entities

### 1. FileChange

ファイル変更の種類を表す列挙型。

```python
from enum import Enum

class FileChangeType(Enum):
    """ファイル変更の種類"""
    ADDED = "added"      # 新規追加
    UPDATED = "updated"  # 内容更新
    # DELETED: 削除済み（Issue #15で無視に変更、後方互換性のため保持）
    UNCHANGED = "unchanged"  # 変更なし
```

### 2. FileChangeInfo

個別ファイル/ディレクトリの変更情報。

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FileChangeInfo:
    """ファイル変更情報"""
    path: Path           # 相対パス（.claude/skills/start-issue/SKILL.md）
    change_type: FileChangeType
    source_path: Path | None = None  # 更新元パス（削除の場合はNone）
```

### 3. UpdateResult

更新操作の結果を表すデータクラス。

```python
from dataclasses import dataclass, field

@dataclass
class UpdateResult:
    """更新操作の結果"""
    skills_changes: list[FileChangeInfo] = field(default_factory=list)
    agents_changes: list[FileChangeInfo] = field(default_factory=list)
    errors: list[tuple[Path, str]] = field(default_factory=list)  # (path, error_message)
    dry_run: bool = False

    @property
    def added_count(self) -> int:
        """追加されたファイル/ディレクトリ数"""
        return sum(
            1 for c in self.skills_changes + self.agents_changes
            if c.change_type == FileChangeType.ADDED
        )

    @property
    def updated_count(self) -> int:
        """更新されたファイル/ディレクトリ数"""
        return sum(
            1 for c in self.skills_changes + self.agents_changes
            if c.change_type == FileChangeType.UPDATED
        )

    # deleted_count: Issue #15で廃止（後方互換性のため残存、常に0を返す）

    @property
    def has_changes(self) -> bool:
        """変更があるか"""
        return self.added_count > 0 or self.updated_count > 0

    @property
    def has_errors(self) -> bool:
        """エラーがあるか"""
        return len(self.errors) > 0

    @property
    def success(self) -> bool:
        """更新が成功したか（エラーなし）"""
        return not self.has_errors
```

## Relationships

```
UpdateResult
├── skills_changes: list[FileChangeInfo]
│   └── FileChangeInfo
│       ├── path: Path
│       ├── change_type: FileChangeType
│       └── source_path: Path | None
├── agents_changes: list[FileChangeInfo]
│   └── FileChangeInfo
│       └── ...
├── errors: list[tuple[Path, str]]
└── dry_run: bool
```

## Validation Rules

### FileChangeInfo

1. `path`は相対パスでなければならない
2. ~~`change_type`が`DELETED`の場合、`source_path`は`None`~~（Issue #15で廃止: 管理外ファイルは無視）
3. `change_type`が`ADDED`または`UPDATED`の場合、`source_path`は必須

### UpdateResult

1. `dry_run=True`の場合、実際のファイル変更は発生しない
2. `errors`が空でない場合、終了コードは非0

## State Transitions

```
[Initial State]
    │
    ▼
[Calculate Changes]  ← dry-run=True → [Display Changes] → [Exit 0]
    │
    │ dry-run=False
    ▼
[Apply Changes]
    │
    ├── Success → [Display Summary] → [Exit 0]
    │
    └── Partial Failure → [Display Summary + Errors] → [Exit 1]
```

## Exit Codes

| Code | Meaning | Condition |
|------|---------|-----------|
| 0 | Success | 更新成功（変更なしも含む） |
| 0 | Success (dry-run) | dry-run完了 |
| 1 | General Error | ファイル操作エラー |
| 2 | Not Initialized | `.claude/`が存在しない |
