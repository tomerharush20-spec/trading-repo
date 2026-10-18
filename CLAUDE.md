# trading-repo

Trading project. Bugs here can lose real money, so safety rules below are non-negotiable.

## Trading Safety Rules

- **Paper trading is the default.** Live trading requires an explicit opt-in (e.g. `TRADING_MODE=live` plus a config flag). Never enable live mode in code, tests, or defaults.
- **Never place real orders** from Claude sessions, scripts, or tests unless the user explicitly asks for that specific action.
- **Risk limits are mandatory** for any execution code: max position size, max order notional, max daily loss, and a kill switch.
- **Backtest before live.** New or changed strategies must be validated on historical data, including fees and slippage, before any live use.
- **No look-ahead bias.** Signals at time `t` may only use data available at `t`.

## Secrets

- Credentials come from environment variables or a secret manager, never from source.
- `.env` files and key files are git-ignored; never commit, print, or log them.
- If a secret is exposed, stop and tell the user to rotate it at the broker.

## Workflow

`/plan` -> `/tdd` -> `/verify` -> `/code-review`

Agents in `.claude/agents/`: `planner`, `tdd-guide`, `code-reviewer`, `security-reviewer`.

## Rules

@.claude/rules/security.md
@.claude/rules/testing.md
@.claude/rules/coding-style.md
@.claude/rules/git-workflow.md
