#!/bin/bash
# review-pr.sh - hachimokuでPRをレビューし、結果に対応
#
# Usage: ./scripts/review-pr.sh [-v|--verbose] [-h|--help] [--review-only|--respond-only]
#
# worktreeディレクトリ内で実行してください。
# 現在のブランチに紐づくPRを自動検出します。

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# カスタムオプション解析（lib_parse_options の前に処理）
_REVIEW_ONLY=false
_RESPOND_ONLY=false
_REMAINING_FOR_MODE=()
for arg in "$@"; do
    case "$arg" in
        --review-only)
            _REVIEW_ONLY=true
            ;;
        --respond-only)
            _RESPOND_ONLY=true
            ;;
        *)
            _REMAINING_FOR_MODE+=("$arg")
            ;;
    esac
done
lib_parse_options ${_REMAINING_FOR_MODE[@]+"${_REMAINING_FOR_MODE[@]}"}

# ヘルプ表示
if lib_should_show_help; then
    lib_show_usage "review-pr.sh" "PRをレビューしてコメントを投稿" "[--review-only|--respond-only]" \
"  --review-only  hachimokuレビューのみ実行（対応はスキップ）
  --respond-only 既存のレビュー結果に対応のみ実行（レビューはスキップ）"
    exit 0
fi

# 不明なオプションのチェック
if ! lib_check_unknown_options 0; then
    exit 1
fi

# 相互排他チェック
if [[ "$_REVIEW_ONLY" == "true" ]] && [[ "$_RESPOND_ONLY" == "true" ]]; then
    echo "⚠️ --review-only と --respond-only は同時に指定できません" >&2
    echo "" >&2
    echo "いずれか一方を指定してください:" >&2
    echo "  ./scripts/review-pr.sh --review-only   # レビューのみ実行" >&2
    echo "  ./scripts/review-pr.sh --respond-only  # 対応のみ実行" >&2
    exit 1
fi

# PR番号を検出
lib_detect_pr_or_exit

# レビュー実行（--respond-only でなければ）
if [[ "$_RESPOND_ONLY" != "true" ]]; then
    echo ""
    echo "🔍 hachimokuレビューを実行中..."
    echo ""

    if ! 8moku "$PR_NUM"; then
        echo "⚠️ hachimokuレビューの実行に失敗しました" >&2
        exit 1
    fi
fi

# レビュー結果に対応（--review-only でなければ）
if [[ "$_REVIEW_ONLY" != "true" ]]; then
    echo ""
    echo "📝 hachimokuレビュー結果に対応中..."
    echo ""

    PROMPT="/respond-review $PR_NUM"

    if ! lib_run_claude "$PROMPT"; then
        exit 1
    fi
fi
