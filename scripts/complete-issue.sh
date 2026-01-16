#!/bin/bash
# complete-issue.sh - 実装完了後にcommit, push, PR作成を実行
#
# Usage: ./scripts/complete-issue.sh [-v|--verbose] [-h|--help]
#
# worktreeディレクトリ内で実行してください。

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# オプション解析
lib_parse_options "$@"

# ヘルプ表示
if lib_should_show_help; then
    lib_show_usage "complete-issue.sh" "実装完了後にcommit, push, PR作成を実行"
    exit 0
fi

# 不明なオプションのチェック
if ! lib_check_unknown_options 0; then
    exit 1
fi

echo "🚀 commit-push-pr を実行中..."
echo ""

PROMPT="以下のスキルを実行してください:

/commit-commands:commit-push-pr

実装された変更をコミットし、リモートにプッシュして、プルリクエストを作成してください。"

if ! lib_run_claude "$PROMPT"; then
    exit 1
fi
