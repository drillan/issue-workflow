---
name: code-quality-gate
description: Ensure complete compliance with code quality standards. Use before commit, before PR creation, or when quality issues are detected.
---

# Code Quality Gate Skill

Ensure complete compliance with code quality standards.

## Trigger Conditions

- Before commit
- Before PR creation
- When quality issues are detected
- When explicitly requested

## Quality Checks

Quality commands are loaded from `.claude/workflow-config.json`:

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
   uv run ruff check --fix .  # Auto-fix
   ```

2. **Ruff Formatter**
   ```bash
   uv run ruff format --check .
   uv run ruff format .  # Auto-format
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

**PASS condition**: All checks complete without errors

```
✓ ruff check: 0 errors
✓ ruff format: No changes needed
✓ mypy: Success: no issues found
```

**FAIL condition**: Any check has errors → Block commit/PR creation

## Report Format

```markdown
## Code Quality Gate Report

### Check Results
| Tool | Status | Details |
|------|--------|---------|
| ruff check | ✓ PASS | 0 errors |
| ruff format | ✓ PASS | No changes |
| mypy | ✓ PASS | No issues |

### Overall Result: PASS
```

## Failure Report Format

```markdown
## Code Quality Gate Report

### Check Results
| Tool | Status | Details |
|------|--------|---------|
| ruff check | ✗ FAIL | 3 errors |
| ruff format | ✓ PASS | No changes |
| mypy | ✗ FAIL | 2 issues |

### Details

#### ruff check errors:
- src/auth.py:10: E501 line too long
- src/auth.py:20: F401 unused import

#### mypy issues:
- src/auth.py:15: error: Incompatible types

### Overall Result: FAIL

Commit blocked. Please fix the issues above.
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
