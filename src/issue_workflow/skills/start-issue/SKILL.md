---
name: start-issue
description: Load a GitHub Issue, create a branch, and develop an implementation plan.
---

# /start-issue

Load a GitHub Issue, create a branch, and develop an implementation plan.

## Usage

```
/start-issue <issue-number> [--force] [--current-branch]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `issue-number` | integer | Yes | GitHub Issue number |
| `--force` | flag | No | Skip plan mode and all interactive confirmations (including TDD user approval) |
| `--current-branch` | flag | No | Skip branch creation, use the current branch |

## Instructions

When the user invokes `/start-issue <number>`, follow these steps:

### Step 1: Load Issue

```bash
gh issue view <number> --json number,title,body,labels,state
```

Verify the issue exists and is open. If not open, warn the user.

### Step 2: Determine Branch Type

**If `--current-branch` is specified, skip this step entirely.**

Based on the issue labels and content, determine the appropriate branch prefix:

| Label | Prefix |
|-------|--------|
| `enhancement`, `feature` | `feat/` |
| `bug` | `fix/` |
| `refactoring`, `refactor` | `refactor/` |
| `documentation`, `docs` | `docs/` |
| `test` | `test/` |
| `chore` | `chore/` |

If no matching label, check title/body for keywords. Default to `feat/`.

### Step 3: Create Branch

**If `--current-branch` is specified, skip branch creation.** Instead, display the current branch name:

```bash
git branch --show-current
```

If the result is empty (detached HEAD), display an error and abort.

**Otherwise (default behavior):**

Generate branch name: `<prefix>/<issue-number>-<normalized-title>`

Normalization rules:
- Lowercase
- Remove special characters
- Replace spaces with hyphens
- Limit to 40 characters

```bash
git checkout -b <branch-name>
```

If branch exists, checkout instead of create.

### Step 4: Plan Implementation

Unless `--force` is specified, enter plan mode before proceeding. With `--force`, execute all phases directly without entering plan mode and without interactive confirmations.

Regardless of `--force`, execute the following phases to create an implementation plan.

First, read the workflow configuration:

```bash
cat .claude/workflow-config.json
```

Check `documentation.ddd.enabled` to determine if DDD workflow is active.

#### Phase 1: Analyze Requirements

1. Extract requirements from issue body
2. Identify acceptance criteria
3. Clarify any ambiguous requirements with user

#### Phase 2: Identify Impact Scope

1. Identify affected code files
2. Identify affected documentation using **doc-updater skill** detection patterns:

| Change Type | Documentation Impact |
|-------------|---------------------|
| New CLI option | README, `--help` output |
| API endpoint added/changed | API documentation |
| Configuration option added | Config guide |
| Environment variable added | Setup guide |
| Feature added | Feature documentation |

Target documents are defined in `documentation.paths` from workflow config.

#### Phase 3: Document-Driven Development (DDD)

**Skip this phase if `documentation.ddd.enabled` is false.**

Before implementation, update documentation as specification using **doc-updater skill**:

1. **Draft documentation changes**
   - Write usage examples for new features
   - Document expected behavior
   - Define configuration options
   - If `documentation.ddd.retcon_writing` is true, write documentation as if the feature already exists
     - Purpose: Produces clearer, more confident documentation
     - Example: "Run `--format json`" instead of "will allow users to..."

2. **Update target documents** (from `documentation.paths`):
   - `README.md` - Usage and examples
   - `docs/` - Detailed documentation
   - CLI `--help` text (in code comments)
   - `CHANGELOG.md` (from `documentation.changelog`) if applicable

3. **Review documentation with user**
   - Documentation becomes the "contract" for implementation

#### Phase 4: Design Test Cases (TDD Approach)

Based on the documented specification, design test cases using **tdd-workflow skill**:

1. Identify test scenarios from documentation
2. Define expected inputs and outputs
3. Consider edge cases documented in Phase 3

**If `--force` is specified:**

Skip all TDD user confirmation steps and execute the Red-Green-Refactor cycle autonomously without user approval:

- Do **not** ask "Do you want me to follow TDD workflow?" — assume yes
- Do **not** wait for user approval of test cases — proceed directly to Red confirmation
- Write tests → confirm failure (Red) → implement (Green) → refactor — all automatically
- Still report test results at each phase, but do not pause for confirmation

**If `--force` is not specified (default):**

Follow the standard TDD workflow with user confirmation:

- Ask the user if they want to follow TDD workflow
- Present test cases and get user approval before proceeding
- Wait for user confirmation at each TDD phase transition

#### Phase 5: Create Implementation Plan

1. List tasks in dependency order
2. Identify potential risks and mitigations
3. Summarize in table format

### Step 5: Report to Issue

Post the plan as a comment on the issue using issue-reporter skill:

```markdown
## Implementation Plan

**Task**: [Issue title]

### Plan
1. [Step 1]
2. [Step 2]
...

### Expected Challenges
- [Challenge 1]

---
*Posted by Claude Code at YYYY-MM-DD HH:MM*
```

## Output Format

```
## Issue #<number>: <title>

### Requirements
[Requirements extracted from issue body]

### Documentation Updates (DDD)
- [ ] [Target document]: [Update description]
- [ ] [Target document]: [Update description]

### Test Plan
- [Test case 1]
- [Test case 2]

### Implementation Plan
1. [Step 1]
2. [Step 2]
...

### Verification
[Verification steps]
```

## Error Handling

| Error | Action |
|-------|--------|
| Issue not found | Display error with `gh issue view` suggestion |
| Issue is closed | Warn user and ask for confirmation |
| gh not authenticated | Display `gh auth login` instruction |
| Uncommitted changes | Ask user to commit or stash changes |
| Branch creation failed | Display error details |
| Detached HEAD with `--current-branch` | Display error: not on a branch, checkout a branch first |
| `workflow-config.json` not found | Display error: "Run `/init` to create configuration." |
| `documentation` section missing | Treat as DDD disabled, inform user |
| `documentation.paths` missing or empty | Display warning about no documentation targets |
| doc-updater/tdd-workflow skill not found | Display error with skill installation guidance |
