#!/usr/bin/env python3
"""Run fresh Codex CLI or Claude Code trials in Linux filesystem namespaces; never grade them."""
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_fixtures", ROOT / "scripts/test-skills.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)

# Built-in Claude Code tools offered in both arms. Collaboration (Task, SendMessage)
# matches Codex multi_agent; web, scheduling, remote and publishing tools are left out.
CLAUDE_TOOLS = "Bash,Read,Edit,Write,Task,SendMessage,Skill,ToolSearch"
CLAUDE_TOKEN_FILE = Path("~/.config/oak/claude-oauth-token")
CLAUDE_TOKEN_HELP = (f"create it with `claude setup-token` and save it, readable only by you, to {CLAUDE_TOKEN_FILE}, "
                     "or set CLAUDE_CODE_OAUTH_TOKEN")


def claude_token(environ, home):
    """Return (token, source): the environment variable wins over the private token file."""
    if environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return environ["CLAUDE_CODE_OAUTH_TOKEN"], "CLAUDE_CODE_OAUTH_TOKEN"
    path = home / CLAUDE_TOKEN_FILE.relative_to("~")
    if not path.is_file():
        return None, None
    fixtures.require(path.stat().st_mode & 0o077 == 0, f"{CLAUDE_TOKEN_FILE} must be readable only by you (chmod 600)")
    return path.read_text().strip() or None, str(CLAUDE_TOKEN_FILE)


def claude_binary(given):
    """Return the exact Claude Code binary: the given path, or the installed claude command resolved."""
    if given is None:
        found = shutil.which("claude")
        fixtures.require(found is not None, "claude is not on PATH; pass --claude-binary")
        given = Path(found)
    binary = given.resolve()
    # Only this file is mounted in the sandbox, so it must be a standalone executable.
    fixtures.require(binary.is_file() and binary.read_bytes()[:4] == b"\x7fELF",
                     f"{binary} is not a standalone Claude Code binary; pass --claude-binary with the native versioned binary")
    return binary


def isolation_command(workspace, private_home, runtime, target):
    # Mount only system runtime, this trial, the harness runtime and a fresh home.
    # HOME retains its original value; no real home, OAK checkout, rubric or other
    # trial is mounted.
    command = ["bwrap", "--unshare-pid", "--unshare-ipc", "--die-with-parent"]
    for path in ("/usr", "/etc"):
        command += ["--ro-bind", path, path]
    resolver = Path("/etc/resolv.conf").resolve()
    if str(resolver) != "/etc/resolv.conf":
        command += ["--ro-bind", str(resolver), str(resolver)]
    for path, link in (("/bin", "usr/bin"), ("/sbin", "usr/sbin"), ("/lib", "usr/lib"), ("/lib64", "usr/lib64")):
        command += ["--symlink", link, path]
    command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--bind", str(private_home), str(Path.home()),
                "--ro-bind", str(runtime), target,
                "--bind", str(workspace), "/workspace", "--chdir", "/workspace"]
    return command


def changes_between(before, after):
    return {path: {"before": before.get(path), "after": after.get(path)}
            for path in sorted(before.keys() | after.keys())
            if not path.startswith(".git/") and before.get(path) != after.get(path)}


def json_rows(path):
    # Only JSON objects are events; other valid JSON lines are ignored. A symlink
    # written by the agent could point outside the trial, so it is never followed.
    if path.is_symlink() or not path.is_file():
        return []
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return [row for row in rows if isinstance(row, dict)]


def workspace_inventory(directory):
    """Hash the workspace without following symlinks or stopping on unreadable files."""
    result = {}
    for path in sorted(directory.rglob("*")):
        name = str(path.relative_to(directory))
        if path.is_symlink():
            result[name] = "symlink:" + os.readlink(path)
        elif path.is_file():
            try:
                result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                result[name] = "unreadable"
    return result


def nested_dicts(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from nested_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from nested_dicts(item)


def checked_uuid(ids, label):
    fixtures.require(len(ids) == 1, f"Expected one exact {label}")
    session_id = ids.pop()
    fixtures.require(str(uuid.UUID(session_id)) == session_id, f"Invalid {label}")
    return session_id


def session_id_from_events(path):
    ids = {event["thread_id"] for event in json_rows(path) if event.get("type") == "thread.started"}
    return checked_uuid(ids, "top-level session UUID")


def resumed_flags(flags, session_id):
    # exec resume lacks -s; reuse all other isolation/config overrides explicitly.
    options = flags[2:-1].copy()
    index = options.index("-s")
    del options[index:index + 2]
    return flags[:2] + ["resume"] + options + ["-c", 'sandbox_mode="danger-full-access"', session_id, "-"]


class Codex:
    name = "codex"
    target = "/opt/codex-runtime"
    default_model = "gpt-6.2-sol"

    def __init__(self, runtime, model):
        self.runtime, self.model = runtime, model or self.default_model

    def validate(self):
        fixtures.require((self.runtime / "bin/codex").is_file(), "Invalid Codex vendor directory")
        fixtures.require((Path.home() / ".codex/auth.json").is_file(), "Codex file-based authentication is required")

    def version(self):
        return subprocess.check_output([str(self.runtime / "bin/codex"), "--version"], text=True).strip()

    def prepare_home(self, private_home):
        state = private_home / ".codex"
        state.mkdir(mode=0o700)
        auth = state / "auth.json"
        shutil.copyfile(Path.home() / ".codex/auth.json", auth)
        auth.chmod(0o600)

    def cleanup(self, private_home):
        (private_home / ".codex/auth.json").unlink(missing_ok=True)

    def env(self):
        return {"PATH": f"{self.target}/codex-path:/usr/bin:/bin"}

    def secret(self):
        return None

    def new_session(self):
        return None

    def flags(self, turn_number, session_id):
        flags = [f"{self.target}/bin/codex", "exec", "--ignore-user-config", "--ignore-rules",
                 "--skip-git-repo-check", "--json", "-s", "danger-full-access", "-m", self.model,
                 "-c", 'model_reasoning_effort="low"', "-c", "features.memories=false",
                 "-c", "features.shell_snapshot=false", "-c", "features.apps=false",
                 "-c", "features.browser_use=false", "-c", "features.computer_use=false",
                 "-c", "features.multi_agent=true", "-c", "features.multi_agent_v2=false",
                 "-c", 'web_search="disabled"', "-"]
        return flags if turn_number == 1 else resumed_flags(flags, session_id)

    def observed_session(self, events):
        return session_id_from_events(events)

    def turn_problem(self, events):
        return None

    def turn_details(self, events):
        return {}

    def evidence(self, dest, private_home, selected):
        catalog_present = False
        skill_read = False
        for event in json_rows(dest / "events.jsonl"):
            item = event.get("item", {})
            if event.get("type") == "item.completed" and f"name: {selected}\n" in item.get("aggregated_output", ""):
                skill_read = True
        for trace in (private_home / ".codex/sessions").rglob("*.jsonl"):
            for row in json_rows(trace):
                payload = row.get("payload", {})
                if row.get("type") == "response_item" and payload.get("role") == "developer":
                    for block in payload.get("content", []):
                        if f"- {selected}:" in block.get("text", ""):
                            catalog_present = True
                if row.get("type") == "response_item" and payload.get("role") == "user":
                    for block in payload.get("content", []):
                        if f"name: {selected}\n" in block.get("text", ""):
                            skill_read = True
        return {"selected_skill_in_catalog": catalog_present, "selected_skill_read_observed": skill_read}

    def conditions(self):
        return {"user_config": False, "memory": False, "web_tools": False}


class Claude:
    name = "claude"
    target = "/opt/claude/claude"

    def __init__(self, runtime, model, token):
        self.runtime, self.model, self.token = runtime, model, token

    def validate(self):
        fixtures.require(self.runtime.is_file(), "Invalid Claude Code binary")
        fixtures.require(bool(self.model), "--model is required for Claude Code")
        fixtures.require(bool(self.token), f"A Claude Code token is required: {CLAUDE_TOKEN_HELP}")

    def version(self):
        return subprocess.check_output([str(self.runtime), "--version"], text=True).strip()

    def prepare_home(self, private_home):
        pass

    def cleanup(self, private_home):
        pass

    def env(self):
        # CLAUDE_CODE_SUBPROCESS_ENV_SCRUB is deliberately absent: it forces the
        # default permission mode, so commands are denied in a non-interactive run.
        return {"PATH": f"{Path(self.target).parent}:/usr/bin:/bin", "CLAUDE_CODE_OAUTH_TOKEN": self.token,
                "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "DISABLE_AUTOUPDATER": "1"}

    def secret(self):
        return self.token

    def new_session(self):
        return str(uuid.uuid4())

    def flags(self, turn_number, session_id):
        return [self.target, "-p", "--output-format", "stream-json", "--verbose", "--strict-mcp-config",
                "--permission-mode", "bypassPermissions", "--permission-prompts", "none",
                "--effort", "low", "--model", self.model, "--tools", CLAUDE_TOOLS,
                "--session-id" if turn_number == 1 else "--resume", session_id]

    def observed_session(self, events):
        rows = json_rows(events)
        ids = {row["session_id"] for row in rows if row.get("session_id") and not row.get("parent_tool_use_id")}
        return checked_uuid(ids, "top-level session UUID")

    def turn_problem(self, events):
        rows = json_rows(events)
        init = next((row for row in rows if row.get("type") == "system" and row.get("subtype") == "init"), None)
        result = next((row for row in reversed(rows) if row.get("type") == "result"), None)
        if init is None or result is None:
            return "missing init or result event"
        if init.get("permissionMode") != "bypassPermissions":
            return f"permission mode {init.get('permissionMode')}"
        if result.get("is_error"):
            return f"result error: {result.get('subtype')}"
        if result.get("permission_denials"):
            return "permission denied: " + ", ".join(sorted({d.get("tool_name", "?") for d in result["permission_denials"]}))
        return None

    def turn_details(self, events):
        rows = json_rows(events)
        result = next((row for row in reversed(rows) if row.get("type") == "result"), {})
        return {"models_used": sorted(result.get("modelUsage", {})), "cost_usd_estimate": result.get("total_cost_usd")}

    def evidence(self, dest, private_home, selected):
        rows = json_rows(dest / "events.jsonl")
        init = next((row for row in rows if row.get("type") == "system" and row.get("subtype") == "init"), {})
        # Listed to the model: the skill_listing attachment in the session transcript.
        catalog_present = any(item.get("type") == "skill_listing" and selected in (item.get("names") or [])
                              for path in sorted((private_home / ".claude/projects").rglob("*.jsonl"))
                              for row in json_rows(path) for item in nested_dicts(row))
        # Read: a successful Read of the pinned file, or Skill call, by the main agent.
        # Subagent activity (parent_tool_use_id) and reads through Bash are not counted.
        pinned = {f"/workspace/{root}/{selected}/SKILL.md" for root in (".agents/skills", ".claude/skills")}
        requested, succeeded = set(), set()
        for path in sorted(dest.glob("events*.jsonl")):
            for row in json_rows(path):
                if row.get("parent_tool_use_id"):
                    continue
                for item in nested_dicts(row):
                    tool_input = item.get("input") if isinstance(item.get("input"), dict) else {}
                    if item.get("type") == "tool_use" and (
                            (item.get("name") == "Read" and os.path.normpath(str(tool_input.get("file_path", ""))) in pinned)
                            or (item.get("name") == "Skill" and tool_input.get("skill") == selected)):
                        requested.add(item.get("id"))
                    elif item.get("type") == "tool_result" and not item.get("is_error"):
                        succeeded.add(item.get("tool_use_id"))
        skill_read = bool(requested & succeeded)
        remote = private_home / ".claude/remote-settings.json"
        try:
            account_settings = ("empty" if not json.loads(remote.read_text()) else "present") \
                if remote.is_file() and not remote.is_symlink() else "absent"
        except ValueError:
            account_settings = "unreadable"
        return {"selected_skill_in_catalog": catalog_present, "selected_skill_read_observed": skill_read,
                "selected_skill_registered": selected in init.get("skills", []),
                "init": {key: init.get(key) for key in ("model", "permissionMode", "tools", "skills", "plugins", "mcp_servers")},
                "account_remote_settings": account_settings}

    def conditions(self):
        return {"user_config": "none local; account-delivered settings recorded in evidence",
                "memory": False, "web_tools": False, "tools": CLAUDE_TOOLS}


def redact(directory, secret):
    """Replace exact occurrences of a credential in retained evidence.

    Return the paths that contained it and the paths that could not be checked.
    """
    leaked, unreadable = [], []
    if not secret:
        return leaked, unreadable
    # Children sort after their parent, so reverse order renames them first.
    for path in sorted(directory.rglob("*"), reverse=True):
        if secret in path.name:
            path.rename(path.with_name(path.name.replace(secret, "[REDACTED]")))
            leaked.append(str(path.relative_to(directory)).replace(secret, "[REDACTED]") + " (name)")
    needle = secret.encode()
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        name = str(path.relative_to(directory))
        try:
            data = path.read_bytes()
            if needle in data:
                path.write_bytes(data.replace(needle, b"[REDACTED]"))
                leaked.append(name)
        except OSError:
            unreadable.append(name)
    return leaked, unreadable


# Home-relative user state that must not be visible inside a trial.
PROBE_HOME_PATHS = (".agents", ".codex/memories", ".codex/skills", ".codex/config.toml", ".codex/AGENTS.md",
                    ".claude/skills", ".claude/CLAUDE.md", ".claude/projects", ".claude/settings.json",
                    ".claude.json", ".config/oak")
PROBE_PATHS = ("/etc/claude-code", "/evaluation.json", "/var/run/docker.sock")


def probe_code():
    """Python source run inside the namespace; prints visible paths and fails if any."""
    return ("from pathlib import Path; import sys; home=Path.home(); "
            f"paths=[home/p for p in {PROBE_HOME_PATHS!r}] + [Path(p) for p in {PROBE_PATHS + (str(ROOT),)!r}]; "
            "seen=[str(p) for p in paths if p.exists() or p.is_symlink()]; print(' '.join(seen)); sys.exit(bool(seen))")


def trial(base, case_id, arm, pair, harness, timeout):
    dest = base / f"{case_id}-{pair}-{arm}"
    fixtures.prepare(case_id, dest, arm)
    # Give repository-scoped modes a real worktree root. Invocation additionally
    # pins the skill file; a Git root alone did not ensure skill selection here.
    subprocess.run(["git", "init", "--quiet", str(dest / "workspace")], check=True, capture_output=True)
    private_home = dest / "private-home"
    private_home.mkdir(mode=0o700)
    harness.prepare_home(private_home)
    # No user config, memories, installed global skills, shell init, hooks or MCP.
    env = {key: os.environ[key] for key in ("HOME", "USER", "LOGNAME", "LANG", "SSL_CERT_FILE", "SSL_CERT_DIR") if key in os.environ}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.update(harness.env())
    command = isolation_command(dest / "workspace", private_home, harness.runtime, harness.target)
    try:
        probe = subprocess.run(command + ["python3", "-c", probe_code()], env=env, capture_output=True, text=True)
        if probe.returncode:
            raise RuntimeError(f"Isolation probe failed for {dest.name}: {probe.stdout.strip() or probe.stderr.strip()}")
    except BaseException:
        harness.cleanup(private_home)
        raise
    start = time.monotonic()
    status = "completed"
    exit_code = None
    turns = []
    requested_session = harness.new_session()
    session_id = None
    case = next(c for c in fixtures.cases() if c["id"] == case_id)
    stages = [{"prompt": (dest / "prompt.txt").read_text(), "before_files": {}}] + case.get("followups", [])
    leaked, unreadable = [], []
    try:
        for turn_number, stage in enumerate(stages, 1):
            suffix = "" if turn_number == 1 else f"-turn-{turn_number}"
            before_external = workspace_inventory(dest / "workspace")
            for path, content in stage.get("before_files", {}).items():
                target = dest / "workspace" / path
                fixtures.require(path in case["files"] and target.resolve().is_relative_to((dest / "workspace").resolve()), "Invalid external fixture path")
                target.write_text(content)
            before_turn = workspace_inventory(dest / "workspace")
            (dest / f"before{suffix}.json").write_text(json.dumps(before_turn, indent=2) + "\n")
            (dest / f"prompt{suffix}.txt").write_text(stage["prompt"])
            event_path = dest / f"events{suffix}.jsonl"
            turn_start = time.monotonic()
            with event_path.open("w") as output, (dest / f"stderr{suffix}.txt").open("w") as errors:
                result = subprocess.run(command + harness.flags(turn_number, session_id or requested_session), input=stage["prompt"],
                                        text=True, stdout=output, stderr=errors, env=env, timeout=timeout)
            exit_code = result.returncode
            after_turn = workspace_inventory(dest / "workspace")
            (dest / f"after{suffix}.json").write_text(json.dumps(after_turn, indent=2) + "\n")
            turn = {"turn": turn_number, "events": event_path.name, "exit_code": exit_code,
                    "elapsed_seconds": round(time.monotonic() - turn_start, 3),
                    "external_changes": changes_between(before_external, before_turn),
                    "agent_changes": changes_between(before_turn, after_turn)}
            turns.append(turn)
            if exit_code:
                status = "failed"
                break
            observed_session = harness.observed_session(event_path)
            expected_session = session_id or requested_session
            fixtures.require(expected_session is None or observed_session == expected_session, "Resume changed top-level session ID")
            session_id = observed_session
            turn["session_id"] = session_id
            turn.update(harness.turn_details(event_path))
            problem = harness.turn_problem(event_path)
            if problem:
                status = "invalid"
                turn["invalid_reason"] = problem
                break
            if turn_number < len(stages) and turn["agent_changes"]:
                status = "stopped-before-followup"
                break
    except subprocess.TimeoutExpired:
        status = "timeout"
    except (ValueError, OSError) as error:
        status = "failed"
        (dest / "runner-error.txt").write_text(str(error) + "\n")
    finally:
        harness.cleanup(private_home)
        # Runs on every exit path, before any evidence is read or retained.
        leaked, unreadable = redact(dest, harness.secret())
    after = workspace_inventory(dest / "workspace")
    before = json.loads((dest / "before.json").read_text())
    changes = changes_between(before, after)
    selected = case["skill"]
    try:
        evidence = harness.evidence(dest, private_home, selected)
    except Exception as error:  # evidence is advisory; never lose the observation record
        evidence = {"evidence_error": repr(error)}
    record = {"case": case_id, "arm": arm, "pair": pair, "harness": harness.name, "model": harness.model,
              "reasoning_effort": "low", "status": status, "exit_code": exit_code,
              "elapsed_seconds": round(time.monotonic() - start, 3),
              "changes": changes, "events": str(dest / "events.jsonl"),
              "turns": turns, "session_id": session_id, "session_requested": requested_session,
              "expected_turns": len(stages),
              "conditions": {"fresh_home": True, "global_oak_skills": False, "filesystem_isolated": True,
                             "network": "shared for model authentication/inference", "multi_agent": True,
                             "git_root": True, "skill_selection": "explicit project-local path in skill arm",
                             **harness.conditions()},
              "evidence": evidence, "credential_redacted_from": leaked, "credential_check_unreadable": unreadable,
              "grading": "not-run"}
    text = json.dumps(record, indent=2)
    if harness.secret():
        # Paths and errors collected during the turns can still carry the credential.
        text = text.replace(harness.secret(), "[REDACTED]")
        record = json.loads(text)
    (dest / "observations.json").write_text(text + "\n")
    warning = (f", credential redacted from {len(leaked)} files" if leaked else "") + \
              (f", {len(unreadable)} files not checked for the credential" if unreadable else "")
    print(f"{dest.name}: {status}, {record['elapsed_seconds']}s, {len(changes)} changed paths{warning}", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--harness", choices=("codex", "claude"), default="codex")
    parser.add_argument("--vendor", type=Path, help="Installed Codex native vendor directory (codex)")
    parser.add_argument("--claude-binary", type=Path, help="Exact Claude Code version binary (claude; default: the installed claude command, resolved)")
    parser.add_argument("--cases", nargs="+", default=["fix-false-positive", "pushback-overclaim", "task-sync-conflict"])
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--model", help=f"Codex default: {Codex.default_model}; required for Claude Code")
    args = parser.parse_args()
    require = fixtures.require
    require(shutil.which("bwrap"), "Linux bubblewrap is required")
    require(args.pairs > 0 and args.jobs > 0 and args.timeout > 0, "Positive pairs/jobs/timeout required")
    require(not args.output.exists(), "Output directory already exists")
    require(set(args.cases) <= {case["id"] for case in fixtures.cases()}, "Unknown scenario")
    require(len(set(args.cases)) == len(args.cases), "Duplicate scenarios")
    if args.harness == "codex":
        require(args.vendor is not None, "--vendor is required for Codex")
        harness = Codex(args.vendor.resolve(), args.model)
    else:
        token, token_source = claude_token(os.environ, Path.home())
        harness = Claude(claude_binary(args.claude_binary), args.model, token)
    harness.validate()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, mode=0o700)
    shutil.copyfile(ROOT / "tests/skills/cases.json", args.output / "corpus-used.json")
    shutil.copyfile(Path(__file__), args.output / "runner-used.py")
    shutil.copyfile(ROOT / "scripts/test-skills.py", args.output / "fixtures-used.py")
    version = harness.version()
    if harness.name == "claude":
        print(f"Claude Code {version} at {harness.runtime}; model {harness.model}; token from {token_source}", flush=True)
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = []
        for case_id in args.cases:
            for pair in range(1, args.pairs + 1):
                # Alternate the order without retrying failed or interrupted trials.
                for arm in (("baseline", "skill") if pair % 2 else ("skill", "baseline")):
                    futures.append(executor.submit(trial, args.output, case_id, arm, pair, harness, args.timeout))
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    summary = {"harness": harness.name, "harness_version": version,
               "trials": sorted(records, key=lambda r: (r["case"], r["pair"], r["arm"]))}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Evidence: {args.output / 'summary.json'}", flush=True)
    if harness.name == "claude" and any(record["status"] == "failed" for record in records):
        print(f"Some trials failed. If the token expired: {CLAUDE_TOKEN_HELP}.", flush=True)


if __name__ == "__main__":
    main()
