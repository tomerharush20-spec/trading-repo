"""Tests for .claude/hooks/broker_guard.py: paper only, and an explicit yes for every broker action."""
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "broker_guard.py"
spec = importlib.util.spec_from_file_location("broker_guard", HOOK)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "trader").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def config(self, **values):
        cfg = {"paper": True, "broker": "alpaca"}
        cfg.update(values)
        (self.root / "trader" / "config.json").write_text(json.dumps(cfg))

    def check(self, tool, tool_input=None):
        return guard.check({"tool_name": tool, "tool_input": tool_input or {}, "cwd": str(self.root)},
                           project_dir=self.root)


class ReadTools(GuardCase):
    def test_alpaca_read_tools_pass(self):
        self.config()
        for tool in ("mcp__alpaca__get_account_info", "mcp__alpaca__get_open_position",
                     "mcp__alpaca__get_orders", "mcp__alpaca__get_stock_snapshot"):
            self.assertIsNone(self.check(tool), tool)

    def test_ibkr_read_tools_pass(self):
        self.assertIsNone(self.check("mcp__Interactive_Brokers_IBKR__get_price_history"))
        self.assertIsNone(self.check("mcp__Interactive_Brokers_IBKR__search_contracts"))

    def test_non_broker_tools_pass(self):
        self.assertIsNone(self.check("Bash", {"command": "ls"}))
        self.assertIsNone(self.check("mcp__trading_view__mcp-tv-get-news"))


class AlpacaOrders(GuardCase):
    def test_order_asks_when_paper_true(self):
        self.config()
        decision, reason = self.check("mcp__alpaca__place_stock_order", {"symbol": "TSLA"})
        self.assertEqual(decision, "ask")
        self.assertIn("paper", reason.lower())

    def test_every_action_tool_asks(self):
        self.config()
        for tool in ("mcp__alpaca__cancel_order_by_id", "mcp__alpaca__replace_order_by_id",
                     "mcp__alpaca__close_position"):
            self.assertEqual(self.check(tool)[0], "ask", tool)

    def test_order_denied_when_paper_false(self):
        self.config(paper=False)
        decision, reason = self.check("mcp__alpaca__place_stock_order")
        self.assertEqual(decision, "deny")
        self.assertIn("paper", reason.lower())

    def test_order_denied_when_paper_is_a_string(self):
        self.config(paper="true")
        self.assertEqual(self.check("mcp__alpaca__place_stock_order")[0], "deny")

    def test_order_denied_without_config(self):
        self.assertEqual(self.check("mcp__alpaca__place_stock_order")[0], "deny")

    def test_order_denied_with_broken_config(self):
        (self.root / "trader" / "config.json").write_text("{not json")
        self.assertEqual(self.check("mcp__alpaca__place_stock_order")[0], "deny")

    def test_bulk_and_risky_tools_always_denied(self):
        self.config()
        for tool in ("mcp__alpaca__close_all_positions", "mcp__alpaca__cancel_all_orders",
                     "mcp__alpaca__place_option_order", "mcp__alpaca__place_crypto_order",
                     "mcp__alpaca__exercise_options_position", "mcp__alpaca__update_account_config"):
            self.assertEqual(self.check(tool)[0], "deny", tool)

    def test_unknown_alpaca_action_asks(self):
        self.config()
        self.assertEqual(self.check("mcp__alpaca__some_new_tool")[0], "ask")


class Ibkr(GuardCase):
    def test_ibkr_order_tools_denied(self):
        self.config()
        for tool in ("mcp__Interactive_Brokers_IBKR__get_order_instructions",
                     "mcp__Interactive_Brokers_IBKR__place_order"):
            self.assertEqual(self.check(tool)[0], "deny", tool)

    def test_ibkr_read_tool_named_order_still_denied(self):
        self.assertEqual(self.check("mcp__Interactive_Brokers_IBKR__get_account_orders")[0], "deny")

    def test_ibkr_account_changes_ask(self):
        self.assertEqual(self.check("mcp__Interactive_Brokers_IBKR__create_saved_screener")[0], "ask")
        self.assertEqual(self.check("mcp__Interactive_Brokers_IBKR__delete_saved_screener")[0], "ask")


class ConfigEdits(GuardCase):
    def path(self):
        return str(self.root / "trader" / "config.json")

    def test_edit_turning_paper_off_denied(self):
        decision, _ = self.check("Edit", {"file_path": self.path(), "old_string": '"paper": true',
                                          "new_string": '"paper": false'})
        self.assertEqual(decision, "deny")

    def test_write_without_paper_true_denied(self):
        self.assertEqual(self.check("Write", {"file_path": self.path(),
                                              "content": json.dumps({"budget": 5000})})[0], "deny")

    def test_write_with_paper_true_passes(self):
        self.assertIsNone(self.check("Write", {"file_path": self.path(),
                                               "content": json.dumps({"paper": True})}))

    def test_other_edits_to_config_pass(self):
        self.assertIsNone(self.check("Edit", {"file_path": self.path(), "old_string": '"budget": 5000',
                                              "new_string": '"budget": 4000'}))

    def test_edits_to_other_files_pass(self):
        self.assertIsNone(self.check("Edit", {"file_path": str(self.root / "notes.md"),
                                              "new_string": '"paper": false'}))

    def test_write_with_invalid_json_denied(self):
        self.assertEqual(self.check("Write", {"file_path": self.path(), "content": "{oops"})[0], "deny")

    def test_multiedit_turning_paper_off_denied(self):
        edits = [{"old_string": "a", "new_string": "b"}, {"old_string": "x", "new_string": '"paper": null'}]
        self.assertEqual(self.check("MultiEdit", {"file_path": self.path(), "edits": edits})[0], "deny")

    def test_shell_turning_paper_off_denied(self):
        cmd = "sed -i 's/\"paper\": true/\"paper\": false/' trader/config.json"
        self.assertEqual(self.check("Bash", {"command": cmd})[0], "deny")

    def test_live_alpaca_env_in_shell_denied(self):
        self.assertEqual(self.check("Bash", {"command": "export ALPACA_PAPER_TRADE=false"})[0], "deny")


class Main(unittest.TestCase):
    def run_main(self, stdin_text):
        out = io.StringIO()
        old = os.sys.stdin
        os.sys.stdin = io.StringIO(stdin_text)
        try:
            with redirect_stdout(out):
                code = guard.main()
        finally:
            os.sys.stdin = old
        return code, out.getvalue()

    def test_deny_prints_decision_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["CLAUDE_PROJECT_DIR"] = tmp
            try:
                code, out = self.run_main(json.dumps({"tool_name": "mcp__alpaca__place_stock_order",
                                                      "tool_input": {}}))
            finally:
                del os.environ["CLAUDE_PROJECT_DIR"]
        self.assertEqual(code, 0)
        doc = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(doc["hookEventName"], "PreToolUse")
        self.assertEqual(doc["permissionDecision"], "deny")

    def test_runs_as_a_script_like_claude_code(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp, COVERAGE_PROCESS_START="")
            run = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(
                {"tool_name": "mcp__alpaca__place_stock_order", "tool_input": {}}),
                capture_output=True, text=True, env=env, timeout=30, check=False)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(json.loads(run.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_allow_prints_nothing(self):
        code, out = self.run_main(json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x"}}))
        self.assertEqual((code, out), (0, ""))

    def test_unparseable_input_prints_nothing(self):
        code, out = self.run_main("not json")
        self.assertEqual((code, out), (0, ""))  # nothing to judge: no tool name at all

    def test_non_object_input_prints_nothing(self):
        self.assertEqual(self.run_main("[1, 2]"), (0, ""))

    def test_internal_error_asks_instead_of_allowing(self):
        original = guard.check
        guard.check = lambda payload: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            code, out = self.run_main(json.dumps({"tool_name": "mcp__alpaca__place_stock_order"}))
        finally:
            guard.check = original
        doc = json.loads(out)["hookSpecificOutput"]
        self.assertEqual((code, doc["permissionDecision"]), (0, "ask"))
        self.assertIn("boom", doc["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main()
