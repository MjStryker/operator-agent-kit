"""Runner safety controls using a fake CLI; these are not behavioral grades."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("live_runner", ROOT / "scripts/run-skill-trials.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class LiveRunnerTest(unittest.TestCase):
    def run_fake_trial(self, directory, wrong_resume=False, early_write=False, probe_error=False):
        source_home = directory / "source-home"
        (source_home / ".codex").mkdir(parents=True)
        (source_home / ".codex/auth.json").write_text("unit-test-auth-placeholder")
        base = directory / "trials"
        base.mkdir()
        case_id = "task-sync-stale-write"
        dest = base / f"{case_id}-1-baseline"
        calls = []

        def fake_run(command, **kwargs):
            if probe_error and command[0] == "bwrap" and "stdout" not in kwargs:
                raise OSError("fake isolation failure")
            if "stdout" in kwargs:
                calls.append(command)
                session_id = "00000000-0000-0000-0000-000000000002" if wrong_resume and len(calls) == 2 else "00000000-0000-0000-0000-000000000001"
                kwargs["stdout"].write(json.dumps({"type": "thread.started", "thread_id": session_id}) + "\n")
                if early_write:
                    (dest / "workspace/docs/tasks/correct-total.md").write_text("early unauthorized write\n")
            return subprocess.CompletedProcess(command, 0)

        try:
            with patch.object(RUNNER.Path, "home", return_value=source_home), patch.object(RUNNER.subprocess, "run", side_effect=fake_run):
                result = RUNNER.trial(base, case_id, "baseline", 1, directory / "vendor", "test-model", 5)
        finally:
            self.assertFalse((dest / "private-home/.codex/auth.json").exists())
        return result, calls

    def test_resume_exact_session_and_separate_external_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls = self.run_fake_trial(Path(tmp))
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(calls), 2)
        self.assertIn("resume", calls[1])
        self.assertEqual(calls[1][-2:], ["00000000-0000-0000-0000-000000000001", "-"])
        self.assertNotIn("--last", calls[1])
        self.assertNotIn("-s", calls[1])
        self.assertEqual(result["turns"][1]["agent_changes"], {})
        self.assertEqual(set(result["turns"][1]["external_changes"]), {"docs/tasks/correct-total.md"})

    def test_wrong_resumed_session_is_failed_and_auth_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls = self.run_fake_trial(Path(tmp), wrong_resume=True)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["status"], "failed")

    def test_early_write_stops_before_acceptance_or_external_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls = self.run_fake_trial(Path(tmp), early_write=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "stopped-before-followup")
        self.assertEqual(len(result["turns"]), 1)
        self.assertEqual(result["turns"][0]["external_changes"], {})

    def test_probe_error_removes_auth_before_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(OSError, "fake isolation failure"):
                self.run_fake_trial(Path(tmp), probe_error=True)


if __name__ == "__main__":
    unittest.main()
