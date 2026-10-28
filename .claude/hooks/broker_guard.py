"""
Claude Code PreToolUse hook: paper trading only, and an explicit yes for every broker action.

  alpaca   read tools (get_/list_/search_) pass. Any other tool asks every time, and is denied
           outright unless trader/config.json exists, parses, and has "paper": true (the boolean).
           Bulk, options, crypto and account-config tools are always denied.
  ibkr     the IBKR connector is a live account: order tools are denied, other changes ask.
  config   no edit, write or shell command may turn "paper" off in trader/config.json, or set
           ALPACA_PAPER_TRADE to false.

"paper": true in the config is a promise, not a switch: the broker connector's own keys and
ALPACA_PAPER_TRADE decide where an order really goes. This hook makes the promise hold for
Claude; keeping paper keys in the connector is the user's side of it.

Run by Claude Code as:  python3 .claude/hooks/broker_guard.py   (hook JSON on stdin)
A block prints the PreToolUse decision JSON on stdout; an allow prints nothing.
An error inside the check asks the user instead of failing silently.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

Result = Optional[tuple]  # noqa: UP045 (runtime alias; X | None needs 3.10, the pack supports 3.8)
# (decision "deny" | "ask", reason) or None to allow

ALPACA_RE = re.compile(r"^mcp__[\w-]*alpaca[\w-]*__(?P<tool>.+)$", re.IGNORECASE)
IBKR_RE = re.compile(r"^mcp__[\w-]*(?:interactive_brokers|ibkr)[\w-]*__(?P<tool>.+)$", re.IGNORECASE)
READ_PREFIXES = ("get_", "list_", "search_", "preview_", "whats_new")

ALPACA_ALWAYS_DENY = {
    "close_all_positions", "cancel_all_orders", "place_option_order", "place_crypto_order",
    "exercise_options_position", "do_not_exercise_options_position", "update_account_config",
}

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
CONFIG_REL = Path("trader") / "config.json"
PAPER_OFF_RE = re.compile(r"""["']?paper["']?\s*[:=]\s*(?:false|0|null|none|["'])""", re.IGNORECASE)
LIVE_ENV_RE = re.compile(r"ALPACA_PAPER_TRADE\s*[=:]\s*[\"']?(?:false|0|no)\b", re.IGNORECASE)


def is_read(tool: str) -> bool:
    return tool.lower().startswith(READ_PREFIXES)


def paper_state(project_dir: Path) -> tuple:
    """(True, "") when trader/config.json says "paper": true, else (False, why not)."""
    path = project_dir / CONFIG_REL
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, f"{CONFIG_REL} is missing"
    except (OSError, ValueError) as e:
        return False, f"{CONFIG_REL} cannot be read ({type(e).__name__})"
    if not isinstance(cfg, dict) or cfg.get("paper") is not True:
        return False, f'{CONFIG_REL} does not have "paper": true'
    return True, ""


def check_alpaca(tool: str, project_dir: Path) -> Result:
    if is_read(tool):
        return None
    if tool in ALPACA_ALWAYS_DENY:
        return "deny", f"Alpaca {tool} is blocked in this project (bulk, options, crypto or account change)."
    ok, why = paper_state(project_dir)
    if not ok:
        return "deny", f"Paper trading only: {why}. No broker action until it is restored."
    return "ask", (f"Broker action: Alpaca {tool}. Paper mode is on in {CONFIG_REL}; confirm the "
                   "connector uses PAPER keys, and approve only the exact order you said yes to.")


def check_ibkr(tool: str) -> Result:
    if is_read(tool) and "order" not in tool.lower():
        return None
    if "order" in tool.lower():
        return "deny", "IBKR is a live account: no order or order-instruction tools from this project."
    return "ask", f"IBKR account change: {tool}. Approve only if you asked for it."


def touches_config(path_text: str) -> bool:
    return Path(path_text).as_posix().endswith(CONFIG_REL.as_posix())


def check_config_edit(tool: str, tool_input: dict) -> Result:
    if not touches_config(str(tool_input.get("file_path", ""))):
        return None
    if tool == "Write":
        try:
            new = json.loads(tool_input.get("content", ""))
        except ValueError:
            new = None
        if isinstance(new, dict) and new.get("paper") is True:
            return None
        return "deny", f'Paper trading only: a new {CONFIG_REL} must keep "paper": true.'
    edits = tool_input.get("edits") or [tool_input]
    if any(PAPER_OFF_RE.search(str(e.get("new_string", ""))) for e in edits):
        return "deny", f'Paper trading only: "paper" stays true in {CONFIG_REL}.'
    return None


def check_shell(command: str) -> Result:
    if LIVE_ENV_RE.search(command):
        return "deny", "Paper trading only: ALPACA_PAPER_TRADE may not be turned off."
    if "config.json" in command and re.search(r"paper[\"']?\s*[:=]\s*(?:false|0)", command, re.IGNORECASE):
        return "deny", f'Paper trading only: "paper" stays true in {CONFIG_REL}.'
    return None


def check(payload: dict, project_dir: Path | None = None) -> Result:
    tool = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input") or {}
    root = Path(project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".")
    m = ALPACA_RE.match(tool)
    if m:
        return check_alpaca(m.group("tool"), root)
    m = IBKR_RE.match(tool)
    if m:
        return check_ibkr(m.group("tool"))
    if tool in EDIT_TOOLS:
        return check_config_edit(tool, tool_input)
    if tool in SHELL_TOOLS:
        return check_shell(str(tool_input.get("command", "")))
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(payload, dict):
        return 0
    try:
        result = check(payload)
    except Exception as e:  # noqa: BLE001  never let the guard crash into a silent allow
        result = ("ask", f"broker_guard failed ({type(e).__name__}: {e}); review this call.")
    if result:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": result[0],
            "permissionDecisionReason": result[1],
        }}))
    return 0


if __name__ == "__main__":  # pragma: no cover  (exercised by the subprocess test)
    sys.exit(main())
