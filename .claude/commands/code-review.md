---
description: Security, trading-safety, and quality review of uncommitted changes.
---

# Code Review

Use the **code-reviewer** agent to review uncommitted changes:

1. Get changed files: `git diff --name-only HEAD`

2. For each changed file, check the code-reviewer agent's checklist:
   - Trading safety (CRITICAL)
   - Security (CRITICAL)
   - Code quality (HIGH)
   - Performance and best practices (MEDIUM)

3. If any change touches credentials, broker clients, order placement, or external input, also run the **security-reviewer** agent.

4. Generate a report with:
   - Severity: CRITICAL, HIGH, MEDIUM, LOW
   - File location and line numbers
   - Issue description
   - Suggested fix

5. Block the commit if CRITICAL or HIGH issues are found.

Never approve code with security vulnerabilities or an unguarded live-trading path.
