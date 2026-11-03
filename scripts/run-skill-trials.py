#!/usr/bin/env python3
"""Run fresh Codex CLI trials in Linux filesystem namespaces; never grade them."""
import argparse
import concurrent.futures
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


def isolation_command(workspace, private_home, vendor):
    # Mount only system runtime, this trial and a fresh home. HOME retains its
    # original value; no real home, OAK checkout, rubric or other trial is mounted.
    command = ["bwrap", "--unshare-pid", "--unshare-ipc", "--die-with-parent"]
    for path in ("/usr", "/etc"):
        command += ["--ro-bind", path, path]
    resolver = Path("/etc/resolv.conf").resolve()
    if str(resolver) != "/etc/resolv.conf":
        command += ["--ro-bind", str(resolver), str(resolver)]
    for path, target in (("/bin", "usr/bin"), ("/sbin", "usr/sbin"), ("/lib", "usr/lib"), ("/lib64", "usr/lib64")):
        command += ["--symlink", target, path]
    command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--bind", str(private_home), str(Path.home()),
                "--ro-bind", str(vendor), "/opt/codex-runtime",
                "--bind", str(workspace), "/workspace", "--chdir", "/workspace"]
    return command


def changes_between(before, after):
    return {path: {"before": before.get(path), "after": after.get(path)}
            for path in sorted(before.keys() | after.keys())
            if not path.startswith(".git/") and before.get(path) != after.get(path)}


def session_id_from_events(path):
    ids = {event["thread_id"] for line in path.read_text().splitlines()
           if (event := json.loads(line)).get("type") == "thread.started"}
    fixtures.require(len(ids) == 1, "Expected one exact top-level session ID")
    session_id = ids.pop()
    fixtures.require(str(uuid.UUID(session_id)) == session_id, "Invalid top-level session UUID")
    return session_id


def resumed_flags(flags, session_id):
    # exec resume lacks -s; reuse all other isolation/config overrides explicitly.
    options = flags[2:-1].copy()
    index = options.index("-s")
    del options[index:index + 2]
    return flags[:2] + ["resume"] + options + ["-c", 'sandbox_mode="danger-full-access"', session_id, "-"]


def trial(base, case_id, arm, pair, vendor, model, timeout):
    dest = base / f"{case_id}-{pair}-{arm}"
    fixtures.prepare(case_id, dest, arm)
    # Give repository-scoped modes a real worktree root. Invocation additionally
    # pins the skill file; a Git root alone did not ensure skill selection here.
    subprocess.run(["git", "init", "--quiet", str(dest / "workspace")], check=True, capture_output=True)
    private_home = dest / "private-home"
    codex_state = private_home / ".codex"
    codex_state.mkdir(parents=True, mode=0o700)
    auth = codex_state / "auth.json"
    shutil.copyfile(Path.home() / ".codex/auth.json", auth)
    auth.chmod(0o600)
    # No user config, memories, installed global skills, shell init, hooks or MCP.
    env = {key: os.environ[key] for key in ("HOME", "USER", "LOGNAME", "LANG", "SSL_CERT_FILE", "SSL_CERT_DIR") if key in os.environ}
    env["PATH"] = "/opt/codex-runtime/codex-path:/usr/bin:/bin"
    command = isolation_command(dest / "workspace", private_home, vendor)
    probe_code = ("from pathlib import Path; import sys; "
                  f"paths=[Path.home()/'.agents/skills', Path.home()/'.codex/memories', Path({str(ROOT)!r}), "
                  "Path('/evaluation.json'), Path('/var/run/docker.sock')]; "
                  "sys.exit(any(path.exists() for path in paths))")
    try:
        probe = subprocess.run(command + ["python3", "-c", probe_code], env=env, capture_output=True)
        if probe.returncode:
            raise RuntimeError(f"Isolation probe failed for {dest.name}")
    except BaseException:
        auth.unlink(missing_ok=True)
        raise
    flags = ["/opt/codex-runtime/bin/codex", "exec", "--ignore-user-config", "--ignore-rules",
             "--skip-git-repo-check", "--json", "-s", "danger-full-access", "-m", model,
             "-c", 'model_reasoning_effort="low"', "-c", "features.memories=false",
             "-c", "features.shell_snapshot=false", "-c", "features.apps=false",
             "-c", "features.browser_use=false", "-c", "features.computer_use=false",
             "-c", "features.multi_agent=true", "-c", "features.multi_agent_v2=false",
             "-c", 'web_search="disabled"', "-"]
    start = time.monotonic()
    status = "completed"
    exit_code = None
    turns = []
    session_id = None
    case = next(c for c in fixtures.cases() if c["id"] == case_id)
    stages = [{"prompt": (dest / "prompt.txt").read_text(), "before_files": {}}] + case.get("followups", [])
    try:
        for turn_number, stage in enumerate(stages, 1):
            suffix = "" if turn_number == 1 else f"-turn-{turn_number}"
            before_external = fixtures.inventory(dest / "workspace")
            for path, content in stage.get("before_files", {}).items():
                target = dest / "workspace" / path
                fixtures.require(path in case["files"] and target.resolve().is_relative_to((dest / "workspace").resolve()), "Invalid external fixture path")
                target.write_text(content)
            before_turn = fixtures.inventory(dest / "workspace")
            (dest / f"before{suffix}.json").write_text(json.dumps(before_turn, indent=2) + "\n")
            (dest / f"prompt{suffix}.txt").write_text(stage["prompt"])
            event_path = dest / f"events{suffix}.jsonl"
            turn_start = time.monotonic()
            with event_path.open("w") as output, (dest / f"stderr{suffix}.txt").open("w") as errors:
                turn_flags = flags if turn_number == 1 else resumed_flags(flags, session_id)
                result = subprocess.run(command + turn_flags, input=stage["prompt"], text=True,
                                        stdout=output, stderr=errors, env=env, timeout=timeout)
            exit_code = result.returncode
            after_turn = fixtures.inventory(dest / "workspace")
            (dest / f"after{suffix}.json").write_text(json.dumps(after_turn, indent=2) + "\n")
            turn = {"turn": turn_number, "events": event_path.name, "exit_code": exit_code,
                    "elapsed_seconds": round(time.monotonic() - turn_start, 3),
                    "external_changes": changes_between(before_external, before_turn),
                    "agent_changes": changes_between(before_turn, after_turn)}
            turns.append(turn)
            if exit_code:
                status = "failed"
                break
            observed_session = session_id_from_events(event_path)
            fixtures.require(session_id is None or observed_session == session_id, "Resume changed top-level session ID")
            session_id = observed_session
            turn["session_id"] = session_id
            if turn_number < len(stages) and turn["agent_changes"]:
                status = "stopped-before-followup"
                break
    except subprocess.TimeoutExpired:
        status = "timeout"
    except (ValueError, OSError) as error:
        status = "failed"
        (dest / "runner-error.txt").write_text(str(error) + "\n")
    finally:
        auth.unlink(missing_ok=True)
    after = fixtures.inventory(dest / "workspace")
    before = json.loads((dest / "before.json").read_text())
    changes = changes_between(before, after)
    selected = next(c["skill"] for c in fixtures.cases() if c["id"] == case_id)
    catalog_present = False
    skill_read = False
    for line in (dest / "events.jsonl").read_text().splitlines():
        event = json.loads(line)
        item = event.get("item", {})
        if event.get("type") == "item.completed" and f"name: {selected}\n" in item.get("aggregated_output", ""):
            skill_read = True
    for trace in (codex_state / "sessions").rglob("*.jsonl"):
        for line in trace.read_text().splitlines():
            row = json.loads(line)
            payload = row.get("payload", {})
            if row.get("type") == "response_item" and payload.get("role") == "developer":
                for block in payload.get("content", []):
                    if f"- {selected}:" in block.get("text", ""):
                        catalog_present = True
            if row.get("type") == "response_item" and payload.get("role") == "user":
                for block in payload.get("content", []):
                    if f"name: {selected}\n" in block.get("text", ""):
                        skill_read = True
    record = {"case": case_id, "arm": arm, "pair": pair, "model": model,
              "reasoning_effort": "low", "status": status, "exit_code": exit_code,
              "elapsed_seconds": round(time.monotonic() - start, 3),
              "changes": changes, "events": str(dest / "events.jsonl"),
              "turns": turns, "session_id": session_id, "expected_turns": len(stages),
              "conditions": {"fresh_home": True, "user_config": False, "memory": False,
                             "global_oak_skills": False, "filesystem_isolated": True,
                             "network": "shared for model authentication/inference", "multi_agent": True,
                             "git_root": True, "selected_skill_in_catalog": catalog_present,
                             "selected_skill_read_observed": skill_read,
                             "skill_selection": "explicit project-local path in skill arm"},
              "grading": "not-run"}
    (dest / "observations.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{dest.name}: {status}, {record['elapsed_seconds']}s, {len(changes)} changed paths", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--vendor", required=True, type=Path, help="Installed Codex native vendor directory")
    parser.add_argument("--cases", nargs="+", default=["fix-false-positive", "pushback-overclaim", "task-sync-conflict"])
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--model", default="gpt-6.1-sol")
    args = parser.parse_args()
    require = fixtures.require
    require(shutil.which("bwrap"), "Linux bubblewrap is required")
    require(args.pairs > 0 and args.jobs > 0 and args.timeout > 0, "Positive pairs/jobs/timeout required")
    require(not args.output.exists(), "Output directory already exists")
    require((args.vendor / "bin/codex").is_file(), "Invalid Codex vendor directory")
    require(set(args.cases) <= {case["id"] for case in fixtures.cases()}, "Unknown scenario")
    require(len(set(args.cases)) == len(args.cases), "Duplicate scenarios")
    require((Path.home() / ".codex/auth.json").is_file(), "Codex file-based authentication is required")
    args.output = args.output.resolve()
    args.vendor = args.vendor.resolve()
    args.output.mkdir(parents=True, mode=0o700)
    shutil.copyfile(ROOT / "tests/skills/cases.json", args.output / "corpus-used.json")
    shutil.copyfile(Path(__file__), args.output / "runner-used.py")
    shutil.copyfile(ROOT / "scripts/test-skills.py", args.output / "fixtures-used.py")
    version = subprocess.check_output([str(args.vendor / "bin/codex"), "--version"], text=True).strip()
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = []
        for case_id in args.cases:
            for pair in range(1, args.pairs + 1):
                # Alternate the order without retrying failed or interrupted trials.
                for arm in (("baseline", "skill") if pair % 2 else ("skill", "baseline")):
                    futures.append(executor.submit(trial, args.output, case_id, arm, pair, args.vendor, args.model, args.timeout))
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    summary = {"harness_version": version, "trials": sorted(records, key=lambda r: (r["case"], r["pair"], r["arm"]))}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Evidence: {args.output / 'summary.json'}", flush=True)


if __name__ == "__main__":
    main()
