---
description: Run build, type, lint, test, and security checks on the current state and produce a PASS/FAIL report.
---

# Verification Command

Run comprehensive verification on the current codebase state. Detect the project's tooling (e.g. `pyproject.toml`, `requirements.txt`, `package.json`) and use the matching commands.

## Instructions

Execute in this order:

1. **Build / Install Check**
   - Ensure dependencies resolve and the project imports/builds
   - If it fails, report errors and STOP

2. **Type Check**
   - Python: `mypy` or `pyright` if configured; TypeScript: `tsc --noEmit`
   - Report errors with file:line

3. **Lint Check**
   - Python: `ruff check .`; JS/TS: the project's lint script

4. **Test Suite**
   - Run all tests with coverage (e.g. `pytest --cov`)
   - Report pass/fail count and coverage percentage

5. **Secrets & Safety Audit**
   - Search for hardcoded keys/tokens and tracked `.env` / credential files
   - Confirm live trading is not enabled by default in config

6. **Debug Output Audit**
   - Search for leftover `print(` / `console.log` in source (not tests)

7. **Git Status**
   - Show uncommitted changes and files modified since last commit

## Output

```
VERIFICATION: [PASS/FAIL]

Build:    [OK/FAIL]
Types:    [OK/X errors]
Lint:     [OK/X issues]
Tests:    [X/Y passed, Z% coverage]
Secrets:  [OK/X found]
Safety:   [OK/live trading enabled by default]
Debug:    [OK/X debug prints]

Ready for PR: [YES/NO]
```

If any critical issues, list them with fix suggestions.

## Arguments

$ARGUMENTS can be:
- `quick` - Only build + types
- `full` - All checks (default)
- `pre-commit` - Checks relevant for commits
- `pre-pr` - Full checks plus the **security-reviewer** agent
