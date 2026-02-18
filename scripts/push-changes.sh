#!/bin/bash
# push-changes.sh - レビュー対応後の変更をコミット、プッシュ
#
# Usage: ./scripts/push-changes.sh [-v|--verbose] [-h|--help]
#
# worktreeディレクトリ内で実行してください。
# PRが既に存在する場合はcommit + pushのみ実行します。
# PRが存在しない場合はcommit + push + PR作成を実行します。

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# オプション解析
lib_parse_options "$@"

# ヘルプ表示
if lib_should_show_help; then
    lib_show_usage "push-changes.sh" "レビュー対応後の変更をコミット、プッシュ"
    exit 0
fi

# 不明なオプションのチェック
if ! lib_check_unknown_options 0; then
    exit 1
fi

echo "🚀 commit-push-pr を実行中..."
echo ""

PROMPT="以下のスキルを実行してください:

/commit-push-pr

レビュー対応後の変更をコミットし、リモートにプッシュしてください。PRが既に存在する場合はPR作成をスキップしてください。"

if ! lib_run_claude "$PROMPT"; then
    exit 1
fi
