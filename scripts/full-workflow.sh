#!/bin/bash
# full-workflow.sh - issue対応の全ワークフローを自動実行
#
# Usage: ./scripts/full-workflow.sh [-v|--verbose] [-h|--help] <issue番号>
# Example: ./scripts/full-workflow.sh 199
# Example: ./scripts/full-workflow.sh -v 199
#
# 以下を順次実行します:
# 1. worktree準備（作成 or 既存検出）
# 2. start-issue（計画立案・実装）
# 3. create-pr（commit + push + PR作成）
# 4. hachimokuレビュー + respond-review + respond-comments + push-changes
# 5. merge-pr（CI待機 → マージ → 後処理）

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=$(lib_get_project_root)

# オプション解析
lib_parse_options "$@"
set -- "${_LIB_REMAINING_ARGS[@]}"

# ヘルプ表示
if lib_should_show_help; then
    lib_show_usage "full-workflow.sh" "issue対応の全ワークフローを自動実行" "<issue番号>"
    exit 0
fi

ISSUE_NUM="${1:-}"

if [[ -z "$ISSUE_NUM" ]]; then
    echo "⚠️ issue番号が必要です" >&2
    echo "" >&2
    echo "使用方法: $0 [-v|--verbose] [-h|--help] <issue番号>" >&2
    echo "例: $0 199" >&2
    echo "例: $0 -v 199" >&2
    exit 1
fi

# 数値チェック
if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
    echo "⚠️ issue番号は数値で指定してください: $ISSUE_NUM" >&2
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
echo "📦 Step 1/5: worktree準備"
echo "───────────────────────────────────────────────────────────────"

WORKTREE_PATH=$(lib_get_worktree_path "$ISSUE_NUM")

if [[ -n "$WORKTREE_PATH" ]]; then
    echo "📁 既存のワークツリーを検出: $WORKTREE_PATH"
else
    echo "🔧 ワークツリーを作成中..."
    if ! "$SCRIPT_DIR/add-worktree.sh" "$ISSUE_NUM"; then
        echo "⚠️ ワークツリーの作成に失敗しました" >&2
        exit 1
    fi

    WORKTREE_PATH=$(lib_get_worktree_path "$ISSUE_NUM")

    if [[ -z "$WORKTREE_PATH" ]]; then
        echo "⚠️ ワークツリーディレクトリが見つかりません" >&2
        exit 1
    fi

    echo "✅ ワークツリー作成完了: $WORKTREE_PATH"
fi

cd "$WORKTREE_PATH"
echo ""

# Step 2: start-issue（計画立案・実装）
echo "📝 Step 2/5: start-issue（計画立案・実装）"
echo "───────────────────────────────────────────────────────────────"

START_ISSUE_FILE="$WORKTREE_PATH/.claude/commands/start-issue.md"

if [[ ! -f "$START_ISSUE_FILE" ]]; then
    echo "⚠️ start-issue.md が見つかりません: $START_ISSUE_FILE" >&2
    exit 1
fi

CONTENT="$(cat "$START_ISSUE_FILE")"
CONTENT_REPLACED="${CONTENT//\$ARGUMENTS/$ISSUE_NUM --force}"

PROMPT_START="以下の指示に従って、issue #${ISSUE_NUM} の作業を開始してください。引数は既に ${ISSUE_NUM} --force として渡されています（プランモードをスキップ）。

${CONTENT_REPLACED}"

if ! lib_run_claude "$PROMPT_START" "no_exec"; then
    echo "⚠️ start-issue の実行に失敗しました" >&2
    exit 1
fi

echo ""
echo "✅ start-issue 完了"
echo ""

# Step 3: create-pr（commit + push + PR作成）
echo "📤 Step 3/5: create-pr（commit + push + PR作成）"
echo "───────────────────────────────────────────────────────────────"

PROMPT_COMPLETE="以下のスキルを実行してください:

/commit-push-pr

実装された変更をコミットし、リモートにプッシュして、プルリクエストを作成してください。"

if ! lib_run_claude "$PROMPT_COMPLETE" "no_exec"; then
    echo "⚠️ create-pr の実行に失敗しました" >&2
    exit 1
fi

echo ""
echo "✅ create-pr 完了"
echo ""

# Step 4: hachimokuレビュー + respond-review + respond-comments
echo "🔍 Step 4/5: hachimokuレビュー + respond-review + respond-comments"
echo "───────────────────────────────────────────────────────────────"

PR_NUM=""
if ! PR_NUM=$(lib_get_pr_number); then
    echo "⚠️ PR情報の取得に失敗しました" >&2
    exit 1
fi

if [[ -z "$PR_NUM" ]]; then
    echo "⚠️ PRが見つかりません。レビューをスキップします。"
else
    echo "📍 PRを検出: #$PR_NUM"

    # Step 4a: hachimokuによるローカルレビュー
    echo "🔍 hachimokuレビューを実行中..."
    if ! 8moku "$PR_NUM"; then
        echo "⚠️ hachimokuレビューの実行に失敗しました" >&2
        exit 1
    fi
    echo "✅ hachimokuレビュー完了"

    echo ""

    # Step 4b: hachimokuレビュー結果への対応
    echo "📝 hachimokuレビュー結果に対応中..."
    PROMPT_RESPOND_REVIEW="/respond-review $PR_NUM"
    if ! lib_run_claude "$PROMPT_RESPOND_REVIEW" "no_exec"; then
        echo "⚠️ respond-review の実行に失敗しました" >&2
        exit 1
    fi
    echo "✅ respond-review 完了"

    echo ""

    # Step 4c: 人間レビューコメントへの対応
    echo "💬 レビューコメントに対応中..."
    PROMPT_RESPOND="/review-pr-comments $PR_NUM"
    if ! lib_run_claude "$PROMPT_RESPOND" "no_exec"; then
        echo "⚠️ respond-comments の実行に失敗しました" >&2
        exit 1
    fi
    echo "✅ respond-comments 完了"

    echo ""

    # Step 4d: レビュー対応後の変更をpush（変更がある場合のみ）
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "📤 レビュー対応後の変更をプッシュ中..."
        PROMPT_PUSH="以下のスキルを実行してください:

/commit-push-pr

レビュー対応後の変更をコミットし、リモートにプッシュしてください。PRが既に存在する場合はPR作成をスキップしてください。"

        if ! lib_run_claude "$PROMPT_PUSH" "no_exec"; then
            echo "⚠️ push-changes の実行に失敗しました" >&2
            exit 1
        fi
        echo "✅ push-changes 完了"
    else
        echo "ℹ️ レビュー対応後の変更はありません。push-changesをスキップします。"
    fi
fi

echo ""

# Step 5: merge-pr（CI待機 → マージ → 後処理）
echo "🔀 Step 5/5: merge-pr（CI待機 → マージ → 後処理）"
echo "───────────────────────────────────────────────────────────────"
echo "   (CIチェック完了まで待機します)"

if [[ -z "$PR_NUM" ]]; then
    echo "⚠️ PRが存在しないためmerge-prをスキップします。"
else
    PROMPT_MERGE="/merge-pr $PR_NUM"
    if ! lib_run_claude "$PROMPT_MERGE" "no_exec"; then
        echo "⚠️ merge-pr の実行に失敗しました" >&2
        exit 1
    fi

    echo ""
    echo "✅ merge-pr 完了"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 Full Workflow 完了: issue #${ISSUE_NUM}"
echo "═══════════════════════════════════════════════════════════════"
