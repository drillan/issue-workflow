#!/bin/bash
# setup-issue.sh - worktree作成 → start-issue実行の複合スクリプト
#
# Usage: ./scripts/setup-issue.sh <issue番号>
# Example: ./scripts/setup-issue.sh 199

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=$(lib_get_project_root)

# 引数チェック
ISSUE_NUM="${1:-}"

if [[ -z "$ISSUE_NUM" ]]; then
    echo "⚠️ issue番号が必要です"
    echo ""
    echo "使用方法: $0 <issue番号>"
    echo "例: $0 199"
    exit 1
fi

# 数値チェック
if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
    echo "⚠️ issue番号は数値で指定してください: $ISSUE_NUM"
    exit 1
fi

# Step 1: 既存のworktreeを確認
WORKTREE_PATH=$(lib_get_worktree_path "$ISSUE_NUM")

if [[ -n "$WORKTREE_PATH" ]]; then
    echo "📁 既存のワークツリーを検出: $WORKTREE_PATH"
else
    # Step 2: add-worktree.sh を実行
    echo "🔧 ワークツリーを作成中..."
    "$SCRIPT_DIR/add-worktree.sh" "$ISSUE_NUM"

    # Step 3: 作成されたディレクトリを検出
    WORKTREE_PATH=$(lib_get_worktree_path "$ISSUE_NUM")

    if [[ -z "$WORKTREE_PATH" ]]; then
        echo "⚠️ ワークツリーディレクトリが見つかりません"
        exit 1
    fi

    echo "✅ ワークツリー作成完了: $WORKTREE_PATH"
fi

# Step 4: start-issue を実行
echo ""
echo "🚀 start-issue を実行中..."
echo ""

START_ISSUE_FILE="$WORKTREE_PATH/.claude/commands/start-issue.md"

if [[ ! -f "$START_ISSUE_FILE" ]]; then
    echo "⚠️ start-issue.md が見つかりません: $START_ISSUE_FILE"
    exit 1
fi

# ファイル内容を読み込み、$ARGUMENTSを置換（常に --force を付与）
CONTENT="$(cat "$START_ISSUE_FILE")"
CONTENT_REPLACED="${CONTENT//\$ARGUMENTS/$ISSUE_NUM --force}"

PROMPT="以下の指示に従って、issue #${ISSUE_NUM} の作業を開始してください。引数は既に ${ISSUE_NUM} --force として渡されています（プランモードをスキップ）。

${CONTENT_REPLACED}"

# worktreeディレクトリで claude -p を実行（自動化スクリプトのため常に --dangerously-skip-permissions）
cd "$WORKTREE_PATH"
exec claude -p "$PROMPT" --dangerously-skip-permissions
