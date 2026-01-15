# Git Conventions

This file is the Single Source of Truth for the project's Git naming conventions.

## Branch Naming

### Format

```
<type>/<issue-number>-<description>
```

### Type Prefixes

| Type | Prefix | Usage |
|------|--------|-------|
| Feature | `feat/` | New feature implementation |
| Bug fix | `fix/` | Bug fixes |
| Refactoring | `refactor/` | Code cleanup/improvement |
| Documentation | `docs/` | Documentation additions/edits |
| Testing | `test/` | Test additions/edits |
| Chore | `chore/` | Config changes, dependency updates, etc. |

### Issue Number

- No zero-padding: `123` (correct), `001` (incorrect)
- Can be omitted if no issue: `feat/add-logging`

### Description

- Write in English
- Hyphen-separated (kebab-case)
- Concise description in 2-4 words
- Lowercase only

### Examples

```
feat/123-add-user-authentication
fix/456-fix-login-error
refactor/789-cleanup-api-client
docs/101-update-readme
test/111-add-e2e-tests
chore/222-update-dependencies
```

### Branch Type Detection (for start-issue)

Mapping for automatic branch type detection from issues:

**GitHub Labels → Prefix:**

| Label | Prefix |
|-------|--------|
| `enhancement`, `feature` | `feat/` |
| `bug` | `fix/` |
| `refactoring`, `refactor` | `refactor/` |
| `documentation`, `docs` | `docs/` |
| `test` | `test/` |
| `chore` | `chore/` |

**Keywords → Prefix (fallback when no labels):**

| Keywords | Prefix |
|----------|--------|
| `bug`, `fix`, `error`, `issue` | `fix/` |
| `refactor`, `cleanup`, `improve`, `reorganize` | `refactor/` |
| `doc`, `readme`, `documentation` | `docs/` |
| `test`, `testing` | `test/` |
| `chore`, `config`, `setup`, `dependency` | `chore/` |
| `add`, `feature`, `implement`, `create`, `new` | `feat/` |

**Default:** `feat/`

## Commit Message

### Format

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type

Same as branch prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Refactoring
- `test`: Testing
- `chore`: Other

### Scope (optional)

- Issue number: `feat(#123): add login feature`
- Module name: `fix(api): handle timeout error`

### Description

- Write in English
- Use imperative mood: "add" not "added"
- Start with lowercase
- No period at the end

### Examples

```
feat(#123): add user authentication

fix(api): handle session expiration correctly

docs: update installation guide

refactor(#456): extract common validation logic

chore: update dependencies to latest versions
```

## Git Worktree

### Format

```
../<project-name>-<branch-name>
```

### Rules

- Location: Parent directory of main repository
- Project name: Use repository directory name (e.g., `my-project`)
- Branch name: Replace `/` with `-`

### Examples

| Branch | Worktree Directory |
|--------|-------------------|
| `feat/123-add-auth` | `../${PROJECT_NAME}-feat-123-add-auth` |
| `fix/456-fix-login` | `../${PROJECT_NAME}-fix-456-fix-login` |
| `refactor/789-cleanup` | `../${PROJECT_NAME}-refactor-789-cleanup` |

### Commands

```bash
# Create worktree for existing branch
git worktree add ../${PROJECT_NAME}-feat-123-add-auth feat/123-add-auth

# Create new branch and worktree simultaneously
git worktree add -b feat/123-add-auth ../${PROJECT_NAME}-feat-123-add-auth

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../${PROJECT_NAME}-feat-123-add-auth
```
