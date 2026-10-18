# Third-Party Notices

Parts of the Claude Code configuration in `.claude/` are adapted from
**everything-claude-code** by Affaan Mustafa (declared license: MIT),
via the fork https://github.com/WorldFlowAI/everything-claude-code
at commit `432485ba6b92c14fb357276a98957f348bcff9ee`.

Upstream: https://github.com/affaan-m/everything-claude-code

| File | Origin |
|------|--------|
| `agents/planner.md` | Copied, plus trading-specific checks |
| `agents/code-reviewer.md` | Adapted for trading code |
| `agents/security-reviewer.md` | Rewritten for trading, based on upstream structure |
| `agents/tdd-guide.md` | Rewritten for trading, based on upstream structure |
| `commands/*.md` | Adapted (language-neutral, trading checks) |
| `rules/*.md` | Adapted |

Upstream hooks, scripts, and MCP configs were intentionally **not** imported.
