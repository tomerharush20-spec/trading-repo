# Git Workflow

## Commit Message Format

```
<type>: <description>

<optional body>
```

Types: feat, fix, refactor, docs, test, chore, perf, ci

## Pull Request Workflow

When creating PRs:
1. Analyze full commit history (not just latest commit)
2. Use `git diff [base-branch]...HEAD` to see all changes
3. Draft a comprehensive PR summary, calling out any change to risk or execution logic
4. Include a test plan
5. Push with `-u` flag if new branch

## Feature Implementation Workflow

1. **Plan first** - `/plan` (planner agent)
2. **TDD** - `/tdd` (tdd-guide agent)
3. **Verify** - `/verify`
4. **Review** - `/trade-review` (code-reviewer, plus security-reviewer for sensitive code)
5. **Commit & push** - conventional commit messages
