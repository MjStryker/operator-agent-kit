#!/usr/bin/env python3
"""Installer safety tests. Every run uses a temporary HOME; real skills are never touched.

Run: python3 -m unittest discover -s tests/install
"""
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
REPOSITORY = "https://github.com/MjStryker/operator-agent-kit"
IS_ROOT = os.geteuid() == 0


def tree(directory):
    """Exact description of a tree: files with hash and mode, links, directories."""
    result = {}
    directory = Path(directory)
    if not directory.exists():
        return None
    for path in sorted(directory.rglob("*")):
        rel = str(path.relative_to(directory))
        if path.is_symlink():
            result[rel] = ("link", os.readlink(path))
        elif path.is_dir():
            result[rel] = ("dir",)
        else:
            result[rel] = ("file", hashlib.sha256(path.read_bytes()).hexdigest(),
                           stat.S_IMODE(path.stat().st_mode))
    return result


def write_skill(directory, name, repository=REPOSITORY, version="0.1", extra=None):
    directory.mkdir(parents=True)
    repo_line = f'  repository: "{repository}"\n' if repository else ""
    (directory / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test\nmetadata:\n{repo_line}  version: \"{version}\"\n---\n\n# {name}\n")
    for rel, content in (extra or {}).items():
        (directory / rel).parent.mkdir(parents=True, exist_ok=True)
        (directory / rel).write_text(content)


def make_writable(path):
    for current, dirs, files in os.walk(path):
        for name in dirs + files:
            target = Path(current) / name
            if not target.is_symlink():
                target.chmod(target.stat().st_mode | stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oak-installer-test-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.claude = self.home / ".claude/skills"
        self.agents = self.home / ".agents/skills"
        self.cursor = self.home / ".cursor/skills"
        self.backups = self.home / ".oak/install/backups"
        self.script = ROOT / "scripts/install-skills.sh"

    def tearDown(self):
        make_writable(self.tmp)
        shutil.rmtree(self.tmp)

    def run_installer(self, *args, answers="", script=None):
        env = {**os.environ, "HOME": str(self.home)}
        env.pop("CODEX_HOME", None)
        env.pop("CLAUDE_CONFIG_DIR", None)
        return subprocess.run(["bash", str(script or self.script), *args], input=answers,
                              capture_output=True, text=True, env=env, cwd=self.tmp)

    def third_party(self):
        write_skill(self.claude / "vendor-tool", "vendor-tool", repository="https://example.com/vendor",
                    extra={"scripts/run.sh": "echo vendor\n"})
        (self.claude / "loose-notes.txt").write_text("keep\n")
        (self.claude / ".hidden").mkdir()
        (self.claude / ".hidden/state").write_text("keep\n")

    def runs(self):
        return sorted(self.backups.glob("*/manifest.json")) if self.backups.exists() else []

    def assert_installed(self, dest, name):
        expected = {k: v[1] for k, v in tree(ROOT / "skills" / name).items() if v[0] == "file"}
        if name == "audit":
            expected.update({f"references/specialists/{k}": v[1]
                             for k, v in tree(ROOT / "agents").items() if v[0] == "file"})
        actual = {k: v[1] for k, v in tree(dest / name).items() if v[0] == "file"}
        self.assertEqual(expected, actual, name)

    # ------------------------------------------------------------ install

    def test_fresh_install_backs_up_and_preserves_third_party(self):
        self.third_party()
        before = tree(self.claude)
        result = self.run_installer("--harness", "claude", answers="\ny\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in SKILLS:
            self.assert_installed(self.claude, name)
        after = tree(self.claude)
        self.assertEqual({k: v for k, v in after.items() if k.split("/")[0] not in SKILLS}, before)
        [manifest] = self.runs()
        self.assertEqual(tree(manifest.parent / "claude/skills"), before)
        data = json.loads(manifest.read_text())
        self.assertEqual(data["status"], "installed")
        self.assertFalse((manifest.parent / ".work").exists())

    def test_unchanged_reinstall_modifies_nothing(self):
        self.assertEqual(self.run_installer("--harness", "claude", answers="\ny\n").returncode, 0)
        before = tree(self.claude)
        result = self.run_installer("--harness", "claude", answers="\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Nothing to change", result.stdout)
        self.assertEqual(tree(self.claude), before)
        self.assertEqual(len(self.runs()), 1)

    def test_update_replaces_only_oak_skill_and_removes_obsolete_files(self):
        write_skill(self.claude / "task", "task", version="0.1", extra={"stale.txt": "old\n"})
        self.third_party()
        result = self.run_installer("--harness", "claude", answers="\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("replace   task 0.1 ->", result.stdout)
        self.assertFalse((self.claude / "task/stale.txt").exists())
        self.assert_installed(self.claude, "task")
        [manifest] = self.runs()
        self.assertTrue((manifest.parent / "claude/skills/task/stale.txt").exists())

    def test_collision_blocks_only_that_skill(self):
        write_skill(self.claude / "task", "task", repository="https://example.com/other")
        (self.claude / "oak").mkdir(parents=True)
        (self.claude / "oak/notes.md").write_text("no frontmatter\n")
        os.symlink(ROOT / "skills/think", self.claude / "think")
        before = {name: tree(self.claude / name) for name in ("task", "oak")}
        result = self.run_installer("--harness", "claude", answers="\ny\n")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("BLOCKED   task", result.stdout)
        self.assertIn("BLOCKED   oak", result.stdout)
        self.assertIn("BLOCKED   think", result.stdout)
        self.assertEqual({name: tree(self.claude / name) for name in ("task", "oak")}, before)
        self.assertTrue((self.claude / "think").is_symlink())
        self.assert_installed(self.claude, "assess")

    def test_renamed_and_retired_skills_are_reported_and_cleaned_only_on_request(self):
        write_skill(self.claude / "take", "take")
        write_skill(self.claude / "retired-skill", "retired-skill")
        write_skill(self.claude / "discover-complex-work", "discover-complex-work",
                    repository="https://example.com/other")
        result = self.run_installer("--harness", "claude", answers="\ni\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("take 0.1, replaced by assess", result.stdout)
        self.assertIn("retired-skill 0.1, no longer in OAK", result.stdout)
        self.assertIn("discover-complex-work: former OAK name, but provenance is not established", result.stdout)
        self.assertTrue((self.claude / "take").exists() and (self.claude / "retired-skill").exists())

        result = self.run_installer("--harness", "claude", answers="\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.claude / "take").exists() or (self.claude / "retired-skill").exists())
        self.assertTrue((self.claude / "discover-complex-work/SKILL.md").exists())
        self.assertTrue((self.runs()[-1].parent / "claude/skills/take/SKILL.md").exists())

    def test_cancel_refusal_and_missing_answers_change_nothing(self):
        self.third_party()
        before = tree(self.home)
        for answers in ("\nn\n", "\n", "", "\nmaybe\n"):
            result = self.run_installer("--harness", "claude", answers=answers)
            self.assertEqual(result.returncode, 1, (answers, result.stdout, result.stderr))
            self.assertEqual(tree(self.home), before, answers)

    def test_yes_flag_cannot_bypass_confirmation(self):
        result = self.run_installer("--harness", "claude", "--yes", answers="\n")
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(tree(self.claude))

    def test_custom_backup_root_is_used(self):
        root = self.tmp / "my-backups"
        result = self.run_installer("--harness", "claude", answers=f"{root}\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(root.glob("*/manifest.json"))), 1)
        self.assertEqual(self.runs(), [])

    def test_default_backup_root_is_offered_and_option_changes_default(self):
        root = self.tmp / "option-backups"
        result = self.run_installer("--harness", "claude", "--backup-root", str(root), answers="\nn\n")
        self.assertIn(f"Backup root [{root}]", result.stdout)
        result = self.run_installer("--harness", "claude", answers="\nn\n")
        self.assertIn(f"Backup root [{self.backups}]", result.stdout)

    def test_dangerous_locations_are_refused(self):
        cases = [
            (["--harness", "claude"], f"{self.claude}/backups\n"),
            (["--harness", "claude"], f"{self.agents}/backups\n"),
            (["--harness", "claude"], f"{self.tmp}/project/.claude/skills/b\n"),
            (["--harness", "claude"], f"{ROOT}/backups\n"),
            (["--harness", "claude"], "relative/backups\n"),
            (["--harness", "claude", str(ROOT / "skills")], "\n"),
            (["--harness", "claude", str(ROOT / "skills/task")], "\n"),
            (["--harness", "claude", str(self.home)], "\n"),
            (["--harness", "claude", str(self.home / ".oak/install")], "\n"),
        ]
        for args, answers in cases:
            before = tree(self.home)
            result = self.run_installer(*args, answers=answers + "y\n")
            self.assertEqual(result.returncode, 2, (args, answers, result.stdout, result.stderr))
            self.assertIn("Refusing", result.stderr)
            self.assertEqual(tree(self.home), before, (args, answers))

    def test_backups_and_work_files_are_never_in_skill_directories(self):
        self.third_party()
        self.assertEqual(self.run_installer("--all", answers="\ny\n").returncode, 0)
        for directory in (self.claude, self.agents, self.cursor):
            for skill_md in directory.rglob("SKILL.md"):
                top = skill_md.relative_to(directory).parts[0]
                self.assertTrue(top in SKILLS or top == "vendor-tool", skill_md)
        self.assertEqual({p.name for p in self.home.iterdir()}, {".claude", ".agents", ".cursor", ".oak"})

    def test_codex_and_chatgpt_share_one_target_and_cursor_duplicates_are_reported(self):
        result = self.run_installer("--harness", "codex,chatgpt,cursor,claude", answers="\nn\n")
        self.assertIn("~/.agents/skills  [codex+chatgpt]", result.stdout)
        self.assertIn("cursor reads OAK skills from several directories", result.stdout)
        self.assertRegex(result.stdout, r"evaluated in|not verified|not detected")

    def test_unevaluated_harness_version_is_reported_as_not_verified(self):
        stub = self.tmp / "bin"
        stub.mkdir()
        (stub / "claude").write_text("#!/bin/sh\necho '9.9.9 (Claude Code)'\n")
        (stub / "claude").chmod(0o755)
        env_path = f"{stub}{os.pathsep}{os.environ['PATH']}"
        result = subprocess.run(["bash", str(self.script), "--harness", "claude"], input="\nn\n",
                                capture_output=True, text=True, cwd=self.tmp,
                                env={**os.environ, "HOME": str(self.home), "PATH": env_path})
        self.assertIn("claude 9.9.9 (Claude Code): compatibility not verified for this version", result.stdout)

    # ------------------------------------------------------------ failures

    def repo_copy(self):
        copy = self.tmp / "oak"
        for part in ("scripts", "skills", "agents"):
            shutil.copytree(ROOT / part, copy / part, ignore=shutil.ignore_patterns("__pycache__"))
        return copy / "scripts/install-skills.sh"

    @unittest.skipIf(IS_ROOT, "permissions are not enforced for root")
    def test_copy_failure_changes_nothing(self):
        script = self.repo_copy()
        self.third_party()
        write_skill(self.claude / "task", "task", version="0.1")
        before = tree(self.claude)
        unreadable = script.parents[1] / "skills/think/SKILL.md"
        unreadable.chmod(0)
        result = self.run_installer("--harness", "claude", answers="\ny\n", script=script)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(tree(self.claude), before)

    @unittest.skipIf(IS_ROOT, "permissions are not enforced for root")
    def test_failure_during_replacement_rolls_back(self):
        self.third_party()
        for name in ("assess", "task"):
            write_skill(self.claude / name, name, version="0.1")
        (self.claude / "task").chmod(0o555)  # its move to another parent fails
        before = tree(self.claude)
        result = self.run_installer("--harness", "claude", answers="\ny\n")
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertIn("rolled back", result.stderr)
        self.assertEqual(tree(self.claude), before)
        manifest = json.loads(self.runs()[0].read_text())
        self.assertEqual(manifest["status"], "rolled-back")

    @unittest.skipIf(IS_ROOT, "permissions are not enforced for root")
    def test_backup_failure_prevents_any_change(self):
        self.third_party()
        before = tree(self.claude)
        mode = (self.claude / "vendor-tool/scripts/run.sh").stat().st_mode
        (self.claude / "vendor-tool/scripts/run.sh").chmod(0)
        result = self.run_installer("--harness", "claude", answers="\ny\n")
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertIn("Backup failed", result.stderr)
        (self.claude / "vendor-tool/scripts/run.sh").chmod(mode)
        self.assertEqual(tree(self.claude), before)

    # ------------------------------------------------------------ restore

    def test_restore_recovers_corrupted_third_party_skills(self):
        self.third_party()
        write_skill(self.claude / "take", "take")
        before = tree(self.claude)
        self.assertEqual(self.run_installer("--harness", "claude", answers="\ny\n").returncode, 0)
        run = self.runs()[0].parent
        (self.claude / "vendor-tool/SKILL.md").write_text("corrupted\n")
        shutil.rmtree(self.claude / "vendor-tool/scripts")
        (self.claude / "loose-notes.txt").unlink()
        result = self.run_installer("--restore", str(run), answers="y\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(tree(self.claude), before)
        pre_restore = [m for m in self.runs() if "pre-restore" in m.parent.name]
        self.assertEqual(len(pre_restore), 1)
        self.assertEqual(json.loads(pre_restore[0].read_text())["status"], "restored")

    def test_restore_of_absent_directory_removes_it(self):
        self.assertEqual(self.run_installer("--harness", "cursor", answers="\ny\n").returncode, 0)
        result = self.run_installer("--restore", str(self.runs()[0].parent), answers="y\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.cursor.exists())

    def test_restore_requires_confirmation(self):
        self.third_party()
        self.assertEqual(self.run_installer("--harness", "claude", answers="\ny\n").returncode, 0)
        after = tree(self.claude)
        for answers in ("", "n\n"):
            result = self.run_installer("--restore", str(self.runs()[0].parent), answers=answers)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(tree(self.claude), after)

    def test_damaged_backup_is_refused(self):
        self.third_party()
        self.assertEqual(self.run_installer("--harness", "claude", answers="\ny\n").returncode, 0)
        run = self.runs()[0].parent
        (run / "claude/skills/vendor-tool/SKILL.md").write_text("tampered\n")
        after = tree(self.claude)
        result = self.run_installer("--restore", str(run), answers="y\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("damaged", result.stderr)
        self.assertEqual(tree(self.claude), after)


if __name__ == "__main__":
    unittest.main()
