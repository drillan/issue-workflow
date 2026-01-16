---
name: tdd-workflow
description: Enforce TDD workflow and ensure proper execution of the Red-Green-Refactor cycle. Use when starting a new feature implementation, bug fix, or refactoring.
---

# TDD Workflow Skill

Enforce TDD workflow and ensure proper execution of the Red-Green-Refactor cycle.

## Trigger Conditions

- When starting a new feature implementation
- When starting a bug fix
- When starting refactoring

## Phases

### Phase 1: Red (Create test and confirm failure)

1. **Create/identify test file**
   - Naming convention: `test_<feature>.py`
   - Location: `tests/` directory

2. **Design test cases**
   - Clearly define expected behavior
   - Consider edge cases
   - Test naming convention: `test_<feature>_<situation>_<expected_result>`

3. **Run test and confirm failure**
   ```bash
   uv run pytest tests/test_<feature>.py -v
   ```

4. **User approval** (required)
   - Present test cases
   - Get approval before proceeding to next phase

### Phase 2: Green (Minimal implementation)

1. **Create implementation file**
   - Focus only on making the test pass
   - Avoid over-engineering

2. **Run test and confirm success**
   ```bash
   uv run pytest tests/test_<feature>.py -v
   ```

3. **Quality checks**
   ```bash
   uv run ruff check --fix . && uv run ruff format . && uv run mypy .
   ```

### Phase 3: Refactor

1. **Improve code**
   - Remove duplication
   - Improve readability

2. **Re-run all tests**
   ```bash
   uv run pytest
   ```

## File Mapping

| Implementation File | Test File |
|---------------------|-----------|
| `src/auth.py` | `tests/test_auth.py` |
| `src/article.py` | `tests/test_article.py` |
| `src/services/user.py` | `tests/test_user.py` |

## Test Naming Convention

`test_<feature>_<situation>_<expected_result>`

Examples:
- `test_login_with_valid_credentials_returns_session`
- `test_login_with_invalid_password_raises_error`
- `test_create_user_with_duplicate_email_fails`

## Enforcement Rules

1. **If test file doesn't exist**
   - Request test file creation before starting implementation
   - Block implementation file edits

2. **If test is not failing (Red)**
   - Confirm test fails as intended
   - Explain that a test that doesn't fail is meaningless

3. **After test succeeds (Green)**
   - Suggest transition to refactoring phase
   - Check if additional test cases are needed

## Quality Gates

- All tests must pass
- Coverage must meet standards
- No errors in static analysis

## Instructions for Claude

When implementing a feature:

1. **Always ask**: "Do you want me to follow TDD workflow?"
2. **If yes**:
   - First, write the test file
   - Show the test to the user
   - Run the test and confirm it fails
   - Get user approval before implementation
   - Implement the minimal code to pass
   - Run tests again
   - Refactor if needed
3. **Track progress**:
   - Mark each phase (Red, Green, Refactor)
   - Report test results at each phase
