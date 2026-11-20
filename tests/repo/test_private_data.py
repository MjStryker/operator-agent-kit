import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/check-private-data.py"
spec = importlib.util.spec_from_file_location("check_private_data", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

# Samples are assembled at runtime so this file does not match its own patterns.
AT = "@"


class ScanTest(unittest.TestCase):
    def kinds(self, text, terms=()):
        return [kind for _, kind in checker.scan(text, list(terms))]

    def test_flags_generic_private_data(self):
        self.assertEqual(self.kinds("mail: someone" + AT + "company.test"), ["email address"])
        self.assertEqual(self.kinds("path " + "/home/" + "alice/notes"), ["home directory path"])
        self.assertEqual(self.kinds("path " + "/Users/" + "alice/notes"), ["home directory path"])
        self.assertEqual(self.kinds("token " + "ghp" + "_" + "a" * 36), ["credential"])
        self.assertEqual(self.kinds("-----BEGIN " + "RSA PRIVATE KEY-----"), ["credential"])

    def test_allows_placeholders(self):
        self.assertEqual(self.kinds("1+name" + AT + "users.noreply.github.com"), [])
        self.assertEqual(self.kinds("someone" + AT + "example.com"), [])
        self.assertEqual(self.kinds("install into ~/.agents/skills"), [])
        self.assertEqual(self.kinds('"id": "task-resume-premise-independence"'), [])

    def test_private_terms_ignore_case(self):
        self.assertEqual(self.kinds("Built for ACME Corp", ["acme"]), ["private term"])
        self.assertEqual(self.kinds("Built for a client", ["acme"]), [])


class CommandTest(unittest.TestCase):
    def run_checker(self, terms_file):
        env = {**os.environ, "OAK_PRIVATE_TERMS": str(terms_file)}
        return subprocess.run(["python3", str(SCRIPT)], capture_output=True, text=True, env=env)

    def test_repository_is_clean_without_terms(self):
        result = self.run_checker(Path(tempfile.gettempdir()) / "oak-missing-private-terms.txt")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_local_terms_fail_the_check(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt") as terms:
            terms.write("# comment\nexplicit-only\n")
            terms.flush()
            result = self.run_checker(terms.name)
        self.assertEqual(result.returncode, 1)
        self.assertIn("private term", result.stdout)


if __name__ == "__main__":
    unittest.main()
