---
name: doc-updater
description: Detect changes that require documentation updates and suggest/execute updates. Use when code changes may impact documentation, during pre-PR creation checklist, or when explicitly requested.
---

# doc-updater

Detect changes that require documentation updates and suggest/execute updates.

## Overview

This skill prevents documentation update oversights when code changes occur. It detects API changes, configuration option additions, feature additions, etc., and suggests updates to related READMEs, API specs, configuration guides, and more.

## Trigger

- When code changes may impact documentation
- When user explicitly requests documentation updates
- During pre-PR creation checklist execution

## Instructions

### Step 1: Analyze Changes

Analyze changes to determine documentation impact:

```bash
# Get changed files
git diff --name-only HEAD~1

# Get detailed diff
git diff HEAD~1
```

### Step 2: Identify Documentation Impact

Detect the following patterns:

| Change Type | Documentation Impact |
|-------------|---------------------|
| New CLI option | `--help` output, README |
| API endpoint added/changed | API documentation |
| Configuration option added | Config guide |
| Environment variable added | Setup guide |
| Feature added | Feature documentation |
| Breaking change | Migration guide, CHANGELOG |

### Step 3: Find Related Documents

```bash
# Find documentation files
find . -name "*.md" -type f
find . -name "README*" -type f
find docs/ -type f 2>/dev/null
```

Identify documentation locations:
- `README.md` - Project overview
- `docs/` - Detailed documentation
- `CHANGELOG.md` - Change history
- `API.md` - API specification
- `CONTRIBUTING.md` - Contribution guide

### Step 4: Generate Update Suggestions

Generate update suggestions based on change type:

#### CLI Option Added

```markdown
## Documentation Update Suggestion

### README.md
Add description for `--new-option` option:

```diff
+ ### New Option
+ Use `--new-option` to enable the new feature.
```

### Configuration Change

```markdown
## Documentation Update Suggestion

### docs/configuration.md
Add new configuration option:

```diff
+ ## new_setting
+
+ Type: `boolean`
+ Default: `false`
+
+ Enables the new feature.
```

### Step 5: Execute Updates

After user approval, update documentation:

1. Edit target files
2. Stage changes
3. Preview changes

```bash
# Stage documentation changes
git add README.md docs/
```

## Detection Rules

### Auto-detect Patterns

```python
# CLI options
r"add_argument\s*\(\s*['\"]--(\w+)"
r"Option\s*\(\s*['\"]--(\w+)"
r"typer\.Option\("

# API endpoints
r"@(app|router)\.(get|post|put|delete|patch)"
r"def\s+\w+\s*\(.*request"

# Configuration
r"Config\s*\("
r"settings\.\w+"
r"os\.environ\.get\("

# Environment variables
r"getenv\s*\(\s*['\"](\w+)"
r"environ\[.(\w+).\]"
```

### Changelog Detection

Suggest CHANGELOG updates for the following changes:

- Breaking changes (API signature changes)
- New features
- Bug fixes
- Security patches

## Output Format

### Documentation Impact Report

```
## Documentation Update Check

### Detected Changes
| Type | Impact | Target Document |
|------|--------|-----------------|
| CLI option added | `--format` | README.md |
| Environment variable added | `API_KEY` | docs/setup.md |
| API change | `/users` endpoint | docs/api.md |

### Recommended Actions
1. Add description of new option to README.md
2. Add environment variable setup instructions to docs/setup.md
3. Reflect endpoint changes in docs/api.md

Execute updates? [y/N]
```

### Success

```
✅ Documentation updated

Updated files:
  - README.md (+15 lines)
  - docs/setup.md (+8 lines)
  - CHANGELOG.md (+5 lines)

Next step:
  git commit -m "docs: update documentation for new features"
```

## Error Handling

| Error | Action |
|-------|--------|
| No docs found | `ℹ️ No documentation files found` |
| Doc not writable | `⚠️ No write permission for file` |
| Pattern not found | Suggest manual verification |

## Integration

This skill integrates with:

1. **code-quality-gate** - Documentation check before commit
2. **issue-reporter** - Report documentation update progress
3. **PR Template** - Documentation update checklist

## Best Practices

1. **Update with code changes** - Don't postpone documentation updates
2. **Clarify change scope** - Specifically describe what changed
3. **Include examples** - Add code examples and usage examples
4. **Maintain CHANGELOG** - Record important changes in history
