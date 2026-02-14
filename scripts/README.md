# Scripts

issue対応ワークフローを自動化するスクリプト集です。

## ワークフロー概要

```
./scripts/setup-issue.sh 199     # mainリポジトリで実行
         ↓
    [worktree作成]
         ↓
    [計画立案・実装]
         ↓
./scripts/create-pr.sh      # worktreeで実行
         ↓
    [commit + push + PR作成]
         ↓
./scripts/review-pr.sh           # worktreeで実行
         ↓
    [PRレビュー + コメント投稿]
         ↓
./scripts/respond-comments.sh    # worktreeで実行
         ↓
    [レビューコメントに対応]
         ↓
./scripts/push-changes.sh           # worktreeで実行
         ↓
    [commit + push（PR既存時はPR作成スキップ）]
         ↓
./scripts/merge-pr.sh            # worktreeで実行
         ↓
    [CI待機 → マージ → 後処理]
```

## スクリプト一覧

### setup-issue.sh

worktreeを作成し、issueの計画立案・実装を開始します。

```bash
# mainリポジトリで実行
./scripts/setup-issue.sh <issue番号>

# 例
./scripts/setup-issue.sh 199
```

**実行内容:**
1. `add-worktree.sh` でworktreeを作成
2. worktreeディレクトリに移動
3. `/start-issue` コマンドを実行（--force でプランモードスキップ）

### create-pr.sh

変更をコミット、プッシュしてPRを作成します。

```bash
# worktreeディレクトリで実行
./scripts/create-pr.sh

# 途中経過を表示
./scripts/create-pr.sh -v
```

**実行内容:**
- `/commit-push-pr` コマンドを実行
- 変更をコミット、プッシュ、PR作成

### review-pr.sh

PRをレビューしてコメントを投稿します。

```bash
# worktreeディレクトリで実行
./scripts/review-pr.sh

# レビューのみ実行（対応はしない）
./scripts/review-pr.sh --review-only

# 対応のみ実行（既存のレビュー結果を使用）
./scripts/review-pr.sh --respond-only

# 途中経過を表示
./scripts/review-pr.sh -v
```

**動作モード:**

| モード | オプション | 動作 |
|---|---|---|
| レビュー+対応 | なし（デフォルト） | hachimokuレビュー → `/respond-review`（従来動作） |
| レビューのみ | `--review-only` | hachimokuレビューのみ実行 |
| 対応のみ | `--respond-only` | `/respond-review` のみ実行（既存JSONL使用） |

`--review-only` と `--respond-only` の同時指定はエラーになります。

**実行内容:**
1. `gh pr view` で現在のブランチに紐づくPR番号を自動検出
2. `8moku` でhachimokuレビューを実行（`--respond-only` 時はスキップ）
3. `/respond-review` でレビュー結果に対応（`--review-only` 時はスキップ）

### push-changes.sh

レビュー対応後の変更をコミットしてプッシュします。PRが既に存在する場合はcommit + pushのみ実行し、PR作成をスキップします。

```bash
# worktreeディレクトリで実行
./scripts/push-changes.sh

# 途中経過を表示
./scripts/push-changes.sh -v
```

**実行内容:**
- `/commit-push-pr` コマンドを実行
- PRが既に存在する場合: commit + push のみ
- PRが存在しない場合: commit + push + PR作成

### respond-comments.sh

PRのレビューコメントに対応します。

```bash
# worktreeディレクトリで実行
./scripts/respond-comments.sh

# 途中経過を表示
./scripts/respond-comments.sh -v
```

**実行内容:**
1. `gh pr view` でPR番号を自動検出
2. `/review-pr-comments` コマンドを実行
3. レビューコメントへの対応

### merge-pr.sh

PRをマージします（CI完了待機付き）。

```bash
# worktreeディレクトリで実行
./scripts/merge-pr.sh

# 途中経過を表示
./scripts/merge-pr.sh -v
```

**実行内容:**
1. `gh pr view` でPR番号を自動検出
2. `/merge-pr` コマンドを実行
3. CIチェック完了まで待機
4. squash mergeを実行
5. リモートブランチ削除
6. ローカルブランチ・worktree削除

### full-workflow.sh

上記すべてのステップを一括で実行します。

```bash
# mainリポジトリで実行
./scripts/full-workflow.sh <issue番号>

# 例
./scripts/full-workflow.sh 199

# 途中経過を表示
./scripts/full-workflow.sh -v 199
```

**実行内容:**
1. worktree準備（作成 or 既存検出）
2. start-issue（計画立案・実装）
3. create-pr（commit + push + PR作成）
4. hachimokuレビュー + respond-review + respond-comments + push-changes
5. merge-pr（CI待機 → マージ → 後処理）

### add-worktree.sh

issueに対応するworktreeを作成します（setup-issue.sh から呼び出されます）。

```bash
# mainリポジトリで実行
./scripts/add-worktree.sh <issue番号>

# 例
./scripts/add-worktree.sh 199
```

## 実行場所

| スクリプト | 実行場所 |
|-----------|---------|
| `setup-issue.sh` | mainリポジトリ |
| `add-worktree.sh` | mainリポジトリ |
| `full-workflow.sh` | mainリポジトリ |
| `create-pr.sh` | worktree |
| `review-pr.sh` | worktree |
| `respond-comments.sh` | worktree |
| `push-changes.sh` | worktree |
| `merge-pr.sh` | worktree |

## 前提条件

- `gh` CLI がインストールされていること
- `claude` CLI がインストールされていること
- `jq` がインストールされていること（verboseモードで使用）
- `issue-workflow` コマンドがインストールされていること（`full-workflow.sh` で使用）
- GitHubへの認証が完了していること

## 共通オプション

すべてのスクリプトは以下の共通オプションをサポートしています:

| オプション | 説明 |
|-----------|------|
| `-h`, `--help` | ヘルプを表示 |
| `-v`, `--verbose` | 途中経過を表示（ツール呼び出しを含む）|
