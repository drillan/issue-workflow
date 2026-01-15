# Code Quality Gate Skill

コード品質基準の完全遵守を保証する。

## Trigger Conditions

- コミット前
- PR作成前
- 品質問題検出時
- 明示的な依頼時

## Quality Checks

品質コマンドは`.claude/workflow-config.json`から読み込む:

```json
{
  "quality": {
    "lint": "uv run ruff check --fix .",
    "format": "uv run ruff format .",
    "typecheck": "uv run mypy .",
    "test": "uv run pytest",
    "all": "uv run ruff check --fix . && uv run ruff format . && uv run mypy ."
  }
}
```

### Check Sequence

1. **Ruff Linter**
   ```bash
   uv run ruff check .
   uv run ruff check --fix .  # 自動修正
   ```

2. **Ruff Formatter**
   ```bash
   uv run ruff format --check .
   uv run ruff format .  # 自動フォーマット
   ```

3. **Mypy Type Checker**
   ```bash
   uv run mypy .
   ```

### All-in-One Command

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```

## Gate Criteria

**PASS条件**: すべてのチェックがエラーなしで完了

```
✓ ruff check: 0 errors
✓ ruff format: No changes needed
✓ mypy: Success: no issues found
```

**FAIL条件**: いずれかのチェックでエラー発生 → コミット/PR作成をブロック

## Report Format

```markdown
## Code Quality Gate Report

### チェック結果
| Tool | Status | Details |
|------|--------|---------|
| ruff check | ✓ PASS | 0 errors |
| ruff format | ✓ PASS | No changes |
| mypy | ✓ PASS | No issues |

### 総合判定: PASS
```

## Failure Report Format

```markdown
## Code Quality Gate Report

### チェック結果
| Tool | Status | Details |
|------|--------|---------|
| ruff check | ✗ FAIL | 3 errors |
| ruff format | ✓ PASS | No changes |
| mypy | ✗ FAIL | 2 issues |

### 詳細

#### ruff check errors:
- src/auth.py:10: E501 line too long
- src/auth.py:20: F401 unused import

#### mypy issues:
- src/auth.py:15: error: Incompatible types

### 総合判定: FAIL

コミットをブロックしました。上記の問題を修正してください。
```

## Instructions for Claude

Before committing code:

1. **Check if quality gate is enabled**
   - Read `.claude/workflow-config.json`
   - Check `workflow.quality_gate_required`

2. **If enabled**:
   - Run the `quality.all` command
   - Parse the output
   - If any errors:
     - Block the commit
     - Report the errors
     - Offer to fix automatically
   - If no errors:
     - Allow the commit
     - Report success

3. **Auto-fix behavior**:
   - `ruff check --fix` automatically fixes many issues
   - `ruff format` automatically formats code
   - Re-run checks after fixes
   - Only block if issues remain after auto-fix

## Language-Specific Commands

### Python (default)
```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy .
```

### TypeScript
```bash
npm run lint -- --fix && npm run format && npm run typecheck
```

### Go
```bash
golangci-lint run --fix && go fmt ./... && go vet ./...
```

### Rust
```bash
cargo clippy --fix --allow-dirty --allow-staged && cargo fmt && cargo check
```
