"""Runner safety controls using a fake CLI; these are not behavioral grades."""
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("live_runner", ROOT / "scripts/run-skill-trials.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

CASE_ID = "task-sync-stale-write"
FAKE_TOKEN = "unit-test-claude-token-placeholder"


class LiveRunnerTest(unittest.TestCase):
    def run_fake_trial(self, directory, harness, emit, probe_error=False):
        """Run one trial with subprocess.run replaced; emit(call_number, command, dest) returns event rows."""
        source_home = directory / "source-home"
        (source_home / ".codex").mkdir(parents=True)
        (source_home / ".codex/auth.json").write_text("unit-test-auth-placeholder")
        base = directory / "trials"
        base.mkdir()
        dest = base / f"{CASE_ID}-1-baseline"
        calls = []

        def fake_run(command, **kwargs):
            if probe_error and command[0] == "bwrap" and "stdout" not in kwargs:
                raise OSError("fake isolation failure")
            if "stdout" in kwargs:
                calls.append(command)
                for row in emit(len(calls), command, dest):
                    kwargs["stdout"].write(json.dumps(row) + "\n")
            return subprocess.CompletedProcess(command, 0)

        try:
            with patch.object(RUNNER.Path, "home", return_value=source_home), patch.object(RUNNER.subprocess, "run", side_effect=fake_run):
                result = RUNNER.trial(base, CASE_ID, "baseline", 1, harness, 5)
        finally:
            self.assertFalse((dest / "private-home/.codex/auth.json").exists())
        return result, calls, dest

    # Codex

    def codex_trial(self, directory, wrong_resume=False, early_write=False, probe_error=False):
        def emit(number, command, dest):
            if early_write:
                (dest / "workspace/docs/tasks/correct-total.md").write_text("early unauthorized write\n")
            session_id = "00000000-0000-0000-0000-000000000002" if wrong_resume and number == 2 else "00000000-0000-0000-0000-000000000001"
            return [{"type": "thread.started", "thread_id": session_id}]
        return self.run_fake_trial(directory, RUNNER.Codex(directory / "vendor", "test-model"), emit, probe_error)

    def test_resume_exact_session_and_separate_external_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls, _ = self.codex_trial(Path(tmp))
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
            result, calls, _ = self.codex_trial(Path(tmp), wrong_resume=True)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["status"], "failed")

    def test_early_write_stops_before_acceptance_or_external_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls, _ = self.codex_trial(Path(tmp), early_write=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "stopped-before-followup")
        self.assertEqual(len(result["turns"]), 1)
        self.assertEqual(result["turns"][0]["external_changes"], {})

    def test_probe_error_removes_auth_before_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(OSError, "fake isolation failure"):
                self.codex_trial(Path(tmp), probe_error=True)

    # Claude Code

    def claude_trial(self, directory, wrong_resume=False, mode="bypassPermissions", denied=False, leak=False, after_emit=None):
        harness = RUNNER.Claude(directory / "claude-binary", "test-model", FAKE_TOKEN)

        def emit(number, command, dest):
            if leak:
                (dest / f"workspace/copy-{FAKE_TOKEN}.txt").write_text(FAKE_TOKEN)
            if after_emit:
                after_emit(dest)
            requested = command[-1]
            session_id = "00000000-0000-0000-0000-000000000009" if wrong_resume and number == 2 else requested
            text = f"env shows CLAUDE_CODE_OAUTH_TOKEN={FAKE_TOKEN}" if leak else "proposal only"
            return [{"type": "system", "subtype": "init", "session_id": session_id, "permissionMode": mode,
                     "skills": ["task"], "tools": ["Bash", "Read"]},
                    {"type": "assistant", "session_id": session_id, "message": {"content": [{"type": "text", "text": text}]}},
                    {"type": "result", "subtype": "success", "is_error": False, "session_id": session_id,
                     "permission_denials": [{"tool_name": "Bash"}] if denied else [],
                     "modelUsage": {"test-model": {}}, "total_cost_usd": 0.01}]
        return self.run_fake_trial(directory, harness, emit)

    def test_claude_imposes_then_resumes_exact_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls, _ = self.claude_trial(Path(tmp))
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][-2], "--session-id")
        self.assertEqual(calls[1][-2:], ["--resume", calls[0][-1]])
        self.assertEqual(result["session_id"], calls[0][-1])
        self.assertIn("--tools", calls[0])
        self.assertEqual(result["turns"][0]["models_used"], ["test-model"])

    def test_claude_wrong_resumed_session_is_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls, _ = self.claude_trial(Path(tmp), wrong_resume=True)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["status"], "failed")

    def test_claude_unexpected_permission_mode_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls, _ = self.claude_trial(Path(tmp), mode="default")
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "invalid")
        self.assertIn("permission mode", result["turns"][0]["invalid_reason"])

    def test_claude_permission_denial_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, calls, _ = self.claude_trial(Path(tmp), denied=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "invalid")

    def test_claude_token_is_redacted_from_evidence_names_and_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, _, dest = self.claude_trial(Path(tmp), leak=True)
            retained = b"".join(path.read_bytes() for path in dest.rglob("*") if path.is_file())
            names = [str(path) for path in dest.rglob("*")]
            observations = (dest / "observations.json").read_text()
        self.assertIn("events.jsonl", result["credential_redacted_from"])
        self.assertIn("workspace/copy-[REDACTED].txt (name)", result["credential_redacted_from"])
        self.assertNotIn(FAKE_TOKEN.encode(), retained)
        self.assertFalse([name for name in names if FAKE_TOKEN in name])
        self.assertNotIn(FAKE_TOKEN, json.dumps(result))
        self.assertNotIn(FAKE_TOKEN, observations)
        self.assertIn("copy-[REDACTED].txt", result["changes"])

    def test_unreadable_and_symlinked_workspace_files_are_recorded_not_read(self):
        def plant(dest):
            outside = dest.parent.parent / "host-only.txt"
            outside.write_text("host sentinel")
            (dest / "workspace/link.txt").unlink(missing_ok=True)
            (dest / "workspace/link.txt").symlink_to(outside)
            locked = dest / "workspace/locked.txt"
            if not locked.exists():
                locked.write_text("x")
                locked.chmod(0)

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(RUNNER.Path, "read_bytes", autospec=True, side_effect=self.refuse_host_sentinel):
                result, _, dest = self.claude_trial(Path(tmp), after_emit=plant)
            (dest / "workspace/locked.txt").chmod(0o600)
        self.assertEqual(result["status"], "stopped-before-followup")
        self.assertEqual(result["changes"]["locked.txt"]["after"], "unreadable")
        self.assertTrue(result["changes"]["link.txt"]["after"].startswith("symlink:"))
        self.assertIn("workspace/locked.txt", result["credential_check_unreadable"])

    @staticmethod
    def refuse_host_sentinel(path):
        if path.name == "host-only.txt":
            raise AssertionError("runner followed a symlink outside the trial")
        with open(path, "rb") as handle:
            return handle.read()

    def test_isolation_probe_reports_visible_user_state(self):
        for name in (".agents", ".claude.json", ".claude/settings.json", ".claude/CLAUDE.md",
                     ".codex/config.toml", ".codex/skills", ".codex/AGENTS.md", ".config/oak"):
            self.assertIn(name, RUNNER.PROBE_HOME_PATHS)
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for name in RUNNER.PROBE_HOME_PATHS:
                (home / name).parent.mkdir(parents=True, exist_ok=True)
                (home / name).write_text("marker")
            result = subprocess.run(["python3", "-c", RUNNER.probe_code()], env={**os.environ, "HOME": tmp},
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        for name in RUNNER.PROBE_HOME_PATHS:
            self.assertIn(str(home / name), result.stdout.split())

    def test_claude_nonzero_exit_is_failed_without_observed_session(self):
        harness = RUNNER.Claude(Path("/bin/true"), "test-model", FAKE_TOKEN)
        with tempfile.TemporaryDirectory() as tmp, patch.object(RUNNER.subprocess, "run") as run:
            def fake_run(command, **kwargs):
                return subprocess.CompletedProcess(command, 1 if "stdout" in kwargs else 0)
            run.side_effect = fake_run
            base = Path(tmp) / "trials"
            base.mkdir()
            with patch.object(RUNNER.Path, "home", return_value=Path(tmp)):
                result = RUNNER.trial(base, CASE_ID, "baseline", 1, harness, 5)
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["session_id"])
        self.assertIsNotNone(result["session_requested"])

    def test_claude_evidence_counts_only_successful_main_agent_reads(self):
        def write_rows(path, rows):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(json.dumps(row) + "\n" for row in rows) + "[1, 2]\n")

        def read(tool_id, parent=None, error=False, path="/workspace/.agents/skills/task/SKILL.md"):
            use = {"type": "assistant", "parent_tool_use_id": parent, "message": {"content": [
                {"type": "tool_use", "id": tool_id, "name": "Read", "input": {"file_path": path}}]}}
            result = {"type": "user", "parent_tool_use_id": parent, "message": {"content": [
                {"type": "tool_result", "tool_use_id": tool_id, "is_error": error, "content": "..."}]}}
            return [use, result]

        harness = RUNNER.Claude(Path("/bin/true"), "test-model", FAKE_TOKEN)
        cases = {"main": read("a"), "error": read("b", error=True), "subagent": read("c", parent="task-1"),
                 "claude-copy": read("d", path="/workspace/.claude/skills/task/SKILL.md"),
                 "other-copy": read("e", path="/workspace/other/skills/task/SKILL.md")}
        with tempfile.TemporaryDirectory() as tmp:
            for name, rows in cases.items():
                dest = Path(tmp) / name
                write_rows(dest / "events.jsonl", [{"type": "system", "subtype": "init", "skills": ["task"]}] + rows)
                write_rows(dest / "private-home/.claude/projects/-workspace/s.jsonl",
                           [{"type": "attachment", "attachment": {"type": "skill_listing", "names": ["other"]}}])
                # A listing reached through a symlink outside the trial is ignored.
                write_rows(Path(tmp) / f"outside-{name}.jsonl",
                           [{"type": "attachment", "attachment": {"type": "skill_listing", "names": ["task"]}}])
                (dest / "private-home/.claude/projects/-workspace/link.jsonl").symlink_to(Path(tmp) / f"outside-{name}.jsonl")
                evidence = harness.evidence(dest, dest / "private-home", "task")
                self.assertEqual(evidence["selected_skill_read_observed"], name in ("main", "claude-copy"), name)
                self.assertTrue(evidence["selected_skill_registered"])
                self.assertFalse(evidence["selected_skill_in_catalog"])

    def test_redact_reports_unreadable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "leak.txt").write_text(f"token={FAKE_TOKEN}\n")
            locked = directory / "locked.txt"
            locked.write_text(FAKE_TOKEN)
            locked.chmod(0)
            try:
                leaked, unreadable = RUNNER.redact(directory, FAKE_TOKEN)
            finally:
                locked.chmod(0o600)
            self.assertEqual(leaked, ["leak.txt"])
            self.assertEqual(unreadable, ["locked.txt"])
            self.assertEqual((directory / "leak.txt").read_text(), "token=[REDACTED]\n")

    def test_claude_token_prefers_environment_then_private_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            self.assertEqual(RUNNER.claude_token({}, home), (None, None))
            token_file = home / ".config/oak/claude-oauth-token"
            token_file.parent.mkdir(parents=True)
            token_file.write_text(FAKE_TOKEN + "\n")
            token_file.chmod(0o600)
            self.assertEqual(RUNNER.claude_token({}, home), (FAKE_TOKEN, "~/.config/oak/claude-oauth-token"))
            self.assertEqual(RUNNER.claude_token({"CLAUDE_CODE_OAUTH_TOKEN": "from-env"}, home),
                             ("from-env", "CLAUDE_CODE_OAUTH_TOKEN"))
            token_file.chmod(0o640)
            with self.assertRaisesRegex(ValueError, "readable only by you"):
                RUNNER.claude_token({}, home)

    def test_claude_binary_must_be_standalone_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = Path(tmp) / "claude"
            wrapper.write_text("#!/bin/sh\nexec node cli.js \"$@\"\n")
            with self.assertRaisesRegex(ValueError, "not a standalone"):
                RUNNER.claude_binary(wrapper)
            native = Path(tmp) / "2.1.0"
            native.write_bytes(b"\x7fELF" + b"\0" * 16)
            link = Path(tmp) / "claude-link"
            link.symlink_to(native)
            self.assertEqual(RUNNER.claude_binary(link), native.resolve())

    def test_claude_environment_excludes_scrub_and_carries_token(self):
        env = RUNNER.Claude(Path("/bin/true"), "test-model", FAKE_TOKEN).env()
        self.assertEqual(env["CLAUDE_CODE_OAUTH_TOKEN"], FAKE_TOKEN)
        self.assertNotIn("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB", env)


if __name__ == "__main__":
    unittest.main()
