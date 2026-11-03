"""Preparation isolation and bundle integrity, not agent-behavior assertions."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("audit_fixtures", ROOT / "scripts/test-skills.py")
FIXTURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURES)


class AuditFixtureTest(unittest.TestCase):
    def test_audit_preparation_pins_complete_bundle_and_keeps_oracle_outside(self):
        for case in FIXTURES.cases():
            if case["skill"] != "audit":
                continue
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "trial"
                with contextlib.redirect_stdout(io.StringIO()):
                    FIXTURES.prepare(case["id"], dest, "skill")
                workspace = dest / "workspace"
                expected = FIXTURES.packaged_inventory(ROOT / "skills/audit")
                for harness in (".agents/skills", ".claude/skills"):
                    self.assertEqual(FIXTURES.inventory(workspace / harness / "audit"), expected)
                evaluation = json.loads((dest / "evaluation.json").read_text())
                self.assertEqual(evaluation["skill_source"], expected)
                self.assertTrue(all(c["result"] == "not-run" for c in evaluation["criteria"]))
                allowed = set(case["files"])
                for harness in (".agents/skills", ".claude/skills"):
                    allowed.update(f"{harness}/audit/{path}" for path in expected)
                self.assertEqual(set(FIXTURES.inventory(workspace)), allowed)
                self.assertEqual(json.loads((dest / "before.json").read_text()),
                                 FIXTURES.inventory(workspace))

    def test_quota_followup_events_are_not_leaked_into_initial_workspace(self):
        case = next(c for c in FIXTURES.cases() if c["id"] == "audit-quota-resume")
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "trial"
            with contextlib.redirect_stdout(io.StringIO()):
                FIXTURES.prepare(case["id"], dest, "skill")
            initial = json.loads((dest / "workspace/runtime.json").read_text())
            self.assertEqual(initial["status"], "suspended")
            self.assertIsNone(initial["result"])
            # Verify staged fixture continuity, not runtime/agent resumption behavior.
            for followup in case["followups"]:
                event = json.loads(followup["before_files"]["runtime.json"])
                for key in ("task", "context", "model", "provider"):
                    self.assertEqual(event[key], initial[key])
            self.assertEqual(json.loads(case["followups"][0]["before_files"]["runtime.json"])
                             ["status"], "completed")


if __name__ == "__main__":
    unittest.main()
