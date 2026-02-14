#!/bin/bash
# ~/.claude.json（OAuthトークン）を claude-auth ボリューム内に永続化する
# Claude Code はファイルを atomic write（tmp→rename）するため
# シンボリックリンクではなくコピー＋終了時保存で対応する
PERSIST_FILE="$HOME/.claude/.claude.json.persist"

# 起動時: ボリュームから復元
if [ -f "$PERSIST_FILE" ]; then
    cp "$PERSIST_FILE" "$HOME/.claude.json"
fi

# 終了時: ボリュームに保存
save_auth() {
    if [ -f "$HOME/.claude.json" ]; then
        cp "$HOME/.claude.json" "$PERSIST_FILE"
    fi
}
trap save_auth EXIT

"$@"
