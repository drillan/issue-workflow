# Research: Update Command Implementation

**Date**: 2026-01-15
**Feature**: Update Command
**Spec**: [spec.md](./spec.md)

## Research Questions

### 1. ファイル差分検出方法

**Question**: commands/skillsの差分をどのように検出するか？

**Decision**: Python標準ライブラリ`filecmp`モジュールを使用

**Rationale**:
- `filecmp.cmp(f1, f2, shallow=False)` で内容比較が可能
- `filecmp.dircmp` でディレクトリ比較が可能
- 標準ライブラリなので追加依存なし
- 既存の`shutil`と組み合わせて使用可能

**Alternatives considered**:
- ハッシュ比較（hashlib）: オーバーヘッドが大きい、ファイルサイズが小さいので不要
- 行単位diff（difflib）: 差分詳細表示には有用だが、更新判定には過剰
- Git diff: 外部依存、gitリポジトリ前提になる

**Implementation**:
```python
import filecmp
from pathlib import Path

def get_file_changes(source: Path, target: Path) -> dict[str, list[str]]:
    """差分を検出し、追加/更新/削除ファイルを返す"""
    changes = {"added": [], "updated": [], "deleted": []}

    # 新規・更新ファイル
    for src_file in source.glob("*.md"):
        tgt_file = target / src_file.name
        if not tgt_file.exists():
            changes["added"].append(src_file.name)
        elif not filecmp.cmp(src_file, tgt_file, shallow=False):
            changes["updated"].append(src_file.name)

    # 削除ファイル（ソースにないがターゲットにある）
    for tgt_file in target.glob("*.md"):
        if not (source / tgt_file.name).exists():
            changes["deleted"].append(tgt_file.name)

    return changes
```

### 2. dry-run実装パターン

**Question**: `--dry-run`オプションの最適な実装パターンは？

**Decision**: 差分計算ロジックを分離し、dry-runフラグで実行を制御

**Rationale**:
- 差分計算とファイル操作を明確に分離
- テスト容易性が高い
- 同じ差分表示ロジックを通常実行とdry-runで再利用可能

**Implementation pattern**:
```python
def update_commands_skills(
    claude_dir: Path,
    dry_run: bool = False
) -> UpdateResult:
    """commands/skillsを更新する"""
    # 1. 差分計算（常に実行）
    changes = calculate_changes(claude_dir)

    # 2. 差分表示（常に実行）
    display_changes(changes)

    # 3. 実際の更新（dry-runでない場合のみ）
    if not dry_run:
        apply_changes(changes)

    return UpdateResult(changes=changes, dry_run=dry_run)
```

### 3. 既存TemplateServiceとの統合

**Question**: 既存の`copy_commands`/`copy_skills`を再利用できるか？

**Decision**: 新しいforce overwriteメソッドを追加し、差分検出ロジックを追加

**Rationale**:
- 既存メソッドは「保存（上書きしない）」動作
- updateコマンドは「上書き」動作が必要
- DRY原則に従い、共通部分は抽出

**Implementation approach**:
```python
class TemplateService:
    # 既存メソッド（保存: 上書きしない）
    def copy_commands(self, target_dir: Path) -> Path: ...
    def copy_skills(self, target_dir: Path) -> Path: ...

    # 新規メソッド（上書き: 強制更新）
    def update_commands(self, target_dir: Path, dry_run: bool = False) -> UpdateResult: ...
    def update_skills(self, target_dir: Path, dry_run: bool = False) -> UpdateResult: ...
```

### 4. エラーハンドリング戦略

**Question**: 部分的な更新失敗時の動作は？

**Decision**: エラーをログして続行、最終的に失敗サマリーを表示

**Rationale**:
- 仕様: 「ロールバックしない、既にコピーされたファイルは残る」
- 1ファイルの失敗で全体を止めない
- ユーザーに何が失敗したか明確に伝える

**Implementation**:
```python
@dataclass
class UpdateResult:
    added: list[str]
    updated: list[str]
    deleted: list[str]
    errors: list[tuple[str, str]]  # (filename, error_message)

def apply_changes(...) -> UpdateResult:
    errors = []
    for file in files_to_update:
        try:
            shutil.copy2(src, dst)
        except OSError as e:
            errors.append((file.name, str(e)))
    return UpdateResult(..., errors=errors)
```

### 5. 削除ファイルの扱い

**Question**: ツールキットから削除されたファイルをユーザープロジェクトからも削除するか？

**Decision**: 自動削除は行わない。警告メッセージで通知のみ。

**Rationale**:
- ユーザーがカスタマイズしたファイルを誤って削除するリスク
- 仕様では「上書き」のみ言及、削除は明示されていない
- 安全側に倒す設計
- 将来のv1.2で`--prune`オプションとして検討可能

**Implementation**:
```python
if deleted_files:
    ui.print_warning(
        f"以下のファイルはツールキットに存在しません（手動削除が必要）:\n"
        f"{', '.join(deleted_files)}"
    )
```

### 6. UIフィードバック設計

**Question**: 更新結果をどのように表示するか？

**Decision**: Rich libraryを使用したカラー表示

**Rationale**:
- 既存のui.pyでRichを使用済み
- 追加/更新/削除を色分けで視認性向上
- `--dry-run`時は明確に「[DRY-RUN]」プレフィックス

**Output format**:
```
Updating commands and skills...

Commands:
  [green]+ start-issue.md (added)[/green]
  [yellow]~ merge-pr.md (updated)[/yellow]

Skills:
  [green]+ new-skill/ (added)[/green]
  [yellow]~ tdd-workflow/ (updated)[/yellow]

Updated 1 file, added 2 files.
```

## Summary

| Decision | Choice | Key Reason |
|----------|--------|------------|
| 差分検出 | filecmp | 標準ライブラリ、軽量 |
| dry-run | フラグ制御 | ロジック分離、テスト容易 |
| TemplateService統合 | 新メソッド追加 | DRY、既存機能保持 |
| エラー処理 | 続行+サマリー | 部分成功を許容 |
| 削除ファイル | 警告のみ | 安全優先 |
| UI | Rich colors | 既存スタイル踏襲 |
