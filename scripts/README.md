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
./scripts/complete-issue.sh      # worktreeで実行
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

### complete-issue.sh

実装完了後、変更をコミットしてPRを作成します。

```bash
# worktreeディレクトリで実行
./scripts/complete-issue.sh

# 途中経過を表示
./scripts/complete-issue.sh -v
```

**実行内容:**
- `/commit-commands:commit-push-pr` スキルを実行
- 変更をコミット、プッシュ、PR作成

### review-pr.sh

PRをレビューしてコメントを投稿します。

```bash
# worktreeディレクトリで実行
./scripts/review-pr.sh

# 途中経過を表示
./scripts/review-pr.sh -v
```

**実行内容:**
1. `gh pr view` で現在のブランチに紐づくPR番号を自動検出
2. `/pr-review-toolkit:review-pr` スキルを実行
3. レビュー結果をPRにコメント

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
1. worktree作成 + start-issue（計画立案・実装）
2. complete-issue（commit + push + PR作成）
3. review-pr（PRレビュー + コメント投稿）
4. respond-comments（レビューコメントに対応）
5. merge-pr（CI待機 → マージ → 後処理）

### add-worktree.sh

issueに対応するworktreeを作成します（setup-issue.sh から呼び出されます）。

```bash
# mainリポジトリで実行
./scripts/add-worktree.sh <issue番号>

# 例
./scripts/add-worktree.sh 199
```

### python-init.sh

新しいPythonプロジェクトを初期化します（既存プロジェクトでは使用しません）。

```bash
./scripts/python-init.sh
```

**実行内容:**
- `uv init` でプロジェクト初期化
- 開発ツール（ruff, mypy, pytest）をインストール
- Sphinxドキュメント環境をセットアップ

## 実行場所

| スクリプト | 実行場所 |
|-----------|---------|
| `setup-issue.sh` | mainリポジトリ |
| `add-worktree.sh` | mainリポジトリ |
| `full-workflow.sh` | mainリポジトリ |
| `complete-issue.sh` | worktree |
| `review-pr.sh` | worktree |
| `respond-comments.sh` | worktree |
| `merge-pr.sh` | worktree |

## 前提条件

- `gh` CLI がインストールされていること
- `claude` CLI がインストールされていること
- `jq` がインストールされていること（verboseモードで使用）
- GitHubへの認証が完了していること
