# Plugin Commands Contract

issue-workflowにバンドルされ、`.claude/commands/`にコピーされるスラッシュコマンド。

---

## /start-issue

GitHub Issueを読み込み、ブランチを作成し、実装計画を立案する。

### Synopsis

```
/start-issue <issue番号> [--force]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `issue番号` | integer | Yes | GitHub Issue番号 |
| `--force` | flag | No | 確認なしで実装を開始 |

### Behavior

1. **Issue読み込み**: `gh issue view` でIssue情報を取得
2. **ブランチタイプ決定**: ラベル/キーワードからプレフィックスを判定
3. **ブランチ作成**: 既存の場合は切り替え、新規の場合は作成
4. **計画立案**:
   - `--force`なし: プランモードに移行、ユーザー承認後に実装
   - `--force`あり: 即座に実装開始
5. **Issue報告**: issue-reporterスキルで計画をコメント

### Output

```
## Issue #123: [タイトル]

### 要件
[issueの本文から抽出した要件]

### 実装計画
1. [ステップ1]
2. [ステップ2]
...

### テスト計画
- [テスト項目1]
- [テスト項目2]

### 検証方法
[検証手順]
```

### Errors

| エラー | 対応 |
|--------|------|
| issue番号未指定 | 使用方法を表示 |
| issueが存在しない | `gh issue view`を案内 |
| gh未認証 | `gh auth login`を案内 |
| ブランチ作成失敗 | 原因を表示（未コミット変更等） |

---

## /commit-push-pr

変更のコミット、プッシュ、PR作成を一連で実行する（git-workflow-haikuバンドル）。

### Synopsis

```
/commit-push-pr
```

### Behavior

1. **変更検出**: `git status`で変更を確認
2. **コミット**: 変更内容から適切なコミットメッセージを自動生成
3. **プッシュ**: リモートブランチにプッシュ（`-u`フラグ付き）
4. **PR作成**: `gh pr create`でPRを作成
   - タイトル: ブランチ名からIssue番号とタイトルを推定
   - ベースブランチ: `git symbolic-ref refs/remotes/origin/HEAD`で自動検出（FR-025）

### Output

```
✅ コミット、プッシュ、PR作成が完了しました

コミット: abc1234 feat: add new feature
PR: #300 - Add new feature
URL: https://github.com/owner/repo/pull/300
```

### Errors

| エラー | 対応 |
|--------|------|
| 変更なし | `ℹ️ コミットする変更がありません` |
| プッシュ失敗 | 原因を表示（認証、ネットワーク等） |
| PR作成失敗 | 原因を表示（既存PR、権限等） |

---

## /merge-pr

PRのCIチェックが完了するまで待機し、マージを実行する。

### Synopsis

```
/merge-pr <PR番号> [--merge|--rebase]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PR番号` | integer | Yes | GitHub PR番号 |
| `--merge` | flag | No | マージコミットを作成 |
| `--rebase` | flag | No | リベースマージ |

デフォルト: `--squash`（コミットを1つにまとめる）

### Behavior

1. **PR検証**: 状態、マージ可能性を確認
2. **CI待機**: `gh pr checks --watch`で完了まで待機
3. **マージ実行**: 指定戦略でマージ
4. **後処理**:
   - デフォルトブランチに切り替え（`git symbolic-ref refs/remotes/origin/HEAD`で自動検出、FR-025）
   - リモートブランチ削除（`--delete-branch`）
   - worktree削除（該当する場合）
   - ローカルブランチ削除

### Output

```
✅ PR #100 をマージしました

マージ方法: squash
ベースブランチ: main
リモートブランチ: 削除済み
```

### Errors

| エラー | 対応 |
|--------|------|
| PR番号未指定 | 使用方法を表示 |
| PRが存在しない | エラーメッセージを表示 |
| PRがマージ済み | `ℹ️ PR #N は既にマージ済みです` |
| PRがクローズ済み | `⚠️ PR #N はクローズされています` |
| コンフリクトあり | 解消方法を案内 |
| CIが失敗 | 失敗したチェックを表示 |
| マージがブロック | ブロック理由を表示 |

---

## /add-worktree

Issue用のワークツリーを新規作成する。

### Synopsis

```
/add-worktree <issue番号>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `issue番号` | integer | Yes | GitHub Issue番号 |

### Behavior

1. **Issue読み込み**: Issue情報を取得
2. **ブランチタイプ決定**: ラベル/キーワードから判定
3. **ブランチ名生成**: `<prefix>/<issue番号>-<説明>`
4. **ワークツリー名生成**: `../${PROJECT_NAME}-<branch-name>`
5. **既存確認**: 既に存在する場合はエラー
6. **ワークツリー作成**: `git worktree add -b`

### Output

```
✅ ワークツリーを作成しました

Issue: #200 - [issueタイトル]
ブランチ: feat/200-add-feature
ディレクトリ: ../project-name-feat-200-add-feature

作業を開始するには:
  cd ../project-name-feat-200-add-feature
```

### Errors

| エラー | 対応 |
|--------|------|
| issue番号未指定 | 使用方法を表示 |
| issueが存在しない | エラーメッセージを表示 |
| ワークツリーが既存 | 既存パスを表示 |
| ディレクトリ作成失敗 | 原因を表示 |

---

## /respond-review

hachimoku JSONL出力を読み取り、レビュー指摘に対応する。

### Synopsis

```
/respond-review [PR番号]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PR番号` | integer | No | GitHub PR番号（省略時は現在のブランチから検出） |

### Behavior

1. **PR特定**: 引数または現在のブランチから`gh pr view --json number`で検出
2. **JSONL読み込み**: `.hachimoku/reviews/pr-{number}.jsonl`を読み取り
3. **指摘一覧表示**: 重要度順にテーブル形式で表示
4. **対応方針決定**: 各指摘への対応方針を決定
   - Accept: 修正を実装
   - Reject: 理由を記録してスキップ
5. **修正実施**: Accept指摘に対する修正を実装
6. **コミット**: 修正をコミット

### Output

| # | Severity | File | Line | Description | Decision |
|---|----------|------|------|-------------|----------|
| 1 | Important | path/file.py | 28 | FR-025参照ミス | ✅ Accept |
| 2 | Suggestion | .gitignore | 228 | 末尾改行なし | ✅ Accept |

### Errors

| エラー | 対応 |
|--------|------|
| PR番号が検出できない | `⚠️ 現在のブランチに紐づくPRが見つかりません` |
| JSONLファイルが存在しない | `⚠️ レビュー結果が見つかりません。8moku <番号> を実行してください` |
| JSONLの解析失敗 | `⚠️ レビュー結果ファイルの解析に失敗しました` |

---

## /review-pr-comments

PRのレビューコメント（GitHub上の人間レビューア等）を確認・対応する。

### Synopsis

```
/review-pr-comments [PR番号]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PR番号` | integer | No | GitHub PR番号（省略時は現在のブランチから検出） |

### Behavior

1. **PR特定**: 引数または現在のブランチから検出
2. **コメント取得**: GraphQL/REST APIでスレッド取得
3. **評価テーブル表示**: 各コメントの対応方針を決定
4. **対応実行**:
   - Accept: 修正を実装
   - Reject: 理由を返信してスレッドを解決
5. **サマリー投稿**: PRに対応結果をコメント
6. **コミット**: 変更をコミット

### Output

| Thread ID | File | Issue | Decision | Action |
|-----------|------|-------|----------|--------|
| PRRT_xxx | path/file.py | Description | ✅ Accept / ❌ Reject | Fix / Reply+Resolve |

### Errors

| エラー | 対応 |
|--------|------|
| PR番号が検出できない | `⚠️ 現在のブランチに紐づくPRが見つかりません` |
| PRが存在しない | エラーメッセージを表示 |
