#!/bin/bash
# full-workflow.sh - issue対応の全ワークフローを自動実行
#
# Usage: ./scripts/full-workflow.sh [-v|--verbose] <issue番号>
# Example: ./scripts/full-workflow.sh 199
# Example: ./scripts/full-workflow.sh -v 199
#
# Options:
#   -v, --verbose  途中経過を表示（ツール呼び出しを含む）
#
# 以下を順次実行します:
# 1. worktree作成 + start-issue（計画立案・実装）
# 2. complete-issue（commit + push + PR作成）
# 3. review-pr（PRレビュー + コメント投稿）
# 4. respond-comments（レビューコメントに対応）
# 5. merge-pr（CI待機 → マージ → 後処理）

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=$(lib_get_project_root)

# オプション解析（evalで _LIB_VERBOSE と REMAINING_ARGS を設定）
OUTPUT=$(lib_parse_verbose_option "$@")
# 出力形式を検証してからeval
if [[ ! "$OUTPUT" =~ ^_LIB_VERBOSE=(true|false)\;\ REMAINING_ARGS= ]]; then
    echo "ERROR: Option parsing failed" >&2
    exit 1
fi
eval "$OUTPUT"
eval set -- "$REMAINING_ARGS"

ISSUE_NUM="${1:-}"

if [[ -z "$ISSUE_NUM" ]]; then
    echo "⚠️ issue番号が必要です"
    echo ""
    echo "使用方法: $0 [-v|--verbose] <issue番号>"
    echo "例: $0 199"
    echo "例: $0 -v 199"
    exit 1
fi

# 数値チェック
if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
    echo "⚠️ issue番号は数値で指定してください: $ISSUE_NUM"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 Full Workflow: issue #${ISSUE_NUM}"
if lib_is_verbose; then
    echo "   (verbose mode)"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: worktree作成または検出
echo "📦 Step 1/6: worktree準備"
echo "───────────────────────────────────────────────────────────────"

WORKTREE_PATH=$(lib_get_worktree_path "$ISSUE_NUM")

if [[ -n "$WORKTREE_PATH" ]]; then
    echo "📁 既存のワークツリーを検出: $WORKTREE_PATH"
else
    echo "🔧 ワークツリーを作成中..."
    "$SCRIPT_DIR/add-worktree.sh" "$ISSUE_NUM"

    WORKTREE_PATH=$(lib_get_worktree_path "$ISSUE_NUM")

    if [[ -z "$WORKTREE_PATH" ]]; then
        echo "⚠️ ワークツリーディレクトリが見つかりません"
        exit 1
    fi

    echo "✅ ワークツリー作成完了: $WORKTREE_PATH"
fi

cd "$WORKTREE_PATH"
echo ""

# worktreeに.claude/ディレクトリを初期化
issue-workflow init -l python

# Step 2: start-issue（計画立案・実装）
echo "📝 Step 2/6: start-issue（計画立案・実装）"
echo "───────────────────────────────────────────────────────────────"

START_ISSUE_FILE="$WORKTREE_PATH/.claude/commands/start-issue.md"

if [[ ! -f "$START_ISSUE_FILE" ]]; then
    echo "⚠️ start-issue.md が見つかりません: $START_ISSUE_FILE"
    exit 1
fi

CONTENT="$(cat "$START_ISSUE_FILE")"
CONTENT_REPLACED="${CONTENT//\$ARGUMENTS/$ISSUE_NUM --force}"

PROMPT_START="以下の指示に従って、issue #${ISSUE_NUM} の作業を開始してください。引数は既に ${ISSUE_NUM} --force として渡されています（プランモードをスキップ）。

${CONTENT_REPLACED}"

lib_run_claude "$PROMPT_START" "no_exec"

echo ""
echo "✅ start-issue 完了"
echo ""

# Step 3: complete-issue（commit + push + PR作成）
echo "📤 Step 3/6: complete-issue（commit + push + PR作成）"
echo "───────────────────────────────────────────────────────────────"

PROMPT_COMPLETE="以下のスキルを実行してください:

/commit-commands:commit-push-pr

実装された変更をコミットし、リモートにプッシュして、プルリクエストを作成してください。"

lib_run_claude "$PROMPT_COMPLETE" "no_exec"

echo ""
echo "✅ complete-issue 完了"
echo ""

# Step 4: review-pr（PRレビュー + コメント投稿）
echo "🔍 Step 4/6: review-pr（PRレビュー + コメント投稿）"
echo "───────────────────────────────────────────────────────────────"

PR_NUM=$(gh pr view --json number --jq '.number' 2>/dev/null || true)

if [[ -z "$PR_NUM" ]]; then
    echo "⚠️ PRが見つかりません。review-prをスキップします。"
else
    echo "📍 PRを検出: #$PR_NUM"

    PROMPT_REVIEW="/pr-review-toolkit:review-pr $PR_NUM PRにコメントしてください"
    lib_run_claude "$PROMPT_REVIEW" "no_exec"

    echo ""
    echo "✅ review-pr 完了"
    echo ""

    # Step 5: respond-comments（レビューコメントに対応）
    echo "💬 Step 5/6: respond-comments（レビューコメントに対応）"
    echo "───────────────────────────────────────────────────────────────"

    PROMPT_RESPOND="/review-pr-comments $PR_NUM"
    lib_run_claude "$PROMPT_RESPOND" "no_exec"

    echo ""
    echo "✅ respond-comments 完了"
    echo ""

    # Step 6: merge-pr（CI待機 → マージ → 後処理）
    echo "🔀 Step 6/6: merge-pr（CI待機 → マージ → 後処理）"
    echo "───────────────────────────────────────────────────────────────"
    echo "   (CIチェック完了まで待機します)"

    PROMPT_MERGE="/merge-pr $PR_NUM"
    lib_run_claude "$PROMPT_MERGE" "no_exec"

    echo ""
    echo "✅ merge-pr 完了"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 Full Workflow 完了: issue #${ISSUE_NUM}"
echo "═══════════════════════════════════════════════════════════════"
