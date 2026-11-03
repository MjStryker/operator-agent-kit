#!/usr/bin/env python3
"""Deterministic skill checks and disposable behavioral fixture preparation.

This runner does not invoke or grade a model.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/skills/cases.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(directory):
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def packaged_inventory(directory):
    result = inventory(directory)
    if directory.name == "audit":
        result.update({f"references/specialists/{name}": digest
                       for name, digest in inventory(ROOT / "agents").items()})
    return result


def cases():
    data = json.loads(CORPUS.read_text())
    require(data["schema_version"] == 1, "Unsupported corpus schema")
    return data["cases"]


def check():
    skills = {p.parent.name: p.parent for p in (ROOT / "skills").glob("*/SKILL.md")}
    require(bool(skills), "No skills found")
    for name, directory in skills.items():
        source = (directory / "SKILL.md").read_text()
        require(source.startswith("---\n"), f"{name}: missing YAML frontmatter")
        metadata = yaml.safe_load(source.split("---", 2)[1])
        require(metadata["name"] == name, f"{name}: mismatched name")
        for field in ("description", "license"):
            require(bool(metadata.get(field)), f"{name}: missing {field}")
        for field in ("author", "category", "repository", "status", "version"):
            require(bool(metadata.get("metadata", {}).get(field)), f"{name}: missing metadata.{field}")
        require(metadata["metadata"]["status"] in {"experimental", "active", "deprecated"}, f"{name}: invalid status")
        require(re.fullmatch(r"\d+\.\d+", str(metadata["metadata"]["version"])), f"{name}: invalid version")
        require(metadata.get("disable-model-invocation") is True, f"{name}: explicit-only metadata missing")
        adapter = yaml.safe_load((directory / "agents/openai.yaml").read_text())
        require(adapter.get("policy", {}).get("allow_implicit_invocation") is False, f"{name}: implicit invocation enabled")
        for doc in directory.rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", doc.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                require((doc.parent / target).exists(), f"{doc.relative_to(ROOT)}: broken link {target}")

    agents = ROOT / "agents"
    require(all((agents / name).is_file() for name in
                ("README.md", "common.md", "qa.md", "security.md", "fullstack.md",
                 "ui-ux-react.md", "devops.md")), "Missing reusable specialist definitions")
    for doc in agents.glob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", doc.read_text()):
            if "://" not in target and not target.startswith("#"):
                require((doc.parent / target.split("#", 1)[0]).exists(),
                        f"{doc.relative_to(ROOT)}: broken link {target}")

    corpus = cases()
    ids = set()
    for case in corpus:
        require(case["id"] not in ids and re.fullmatch(r"[a-z0-9-]+", case["id"]), "Invalid/duplicate case id")
        ids.add(case["id"])
        require(case["skill"] in skills, f"{case['id']}: unknown skill")
        require(case["prompt"] and case["checks"] and case["value"], f"{case['id']}: incomplete case")
        require(all((ROOT / path).is_file() for path in case["contracts"]), f"{case['id']}: missing contract")
        require(len({c["id"] for c in case["checks"]}) == len(case["checks"]), f"{case['id']}: duplicate criterion")
        for criterion in case["checks"]:
            require(criterion["scope"] in {"contract", "outcome"}, f"{case['id']}: invalid criterion scope")
            require(type(criterion["blocking"]) is bool and criterion["requirement"], f"{case['id']}: invalid criterion")
        for path in case["files"]:
            require(not Path(path).is_absolute() and ".." not in Path(path).parts, f"{case['id']}: unsafe fixture path")
        for followup in case.get("followups", []):
            require(bool(followup["prompt"]), f"{case['id']}: empty follow-up")
            for path, content in followup.get("before_files", {}).items():
                require(path in case["files"] and isinstance(content, str), f"{case['id']}: invalid follow-up fixture")
    require({c["skill"] for c in corpus} == set(skills), "Every skill needs at least one scenario")

    subprocess.run(["bash", "-n", str(ROOT / "scripts/install-skills.sh")], check=True)
    # Real installation, repeated to exercise replacement, entirely in temporary destinations.
    # Safety cases (collisions, backup, restore, cancellation) are in tests/install/.
    with tempfile.TemporaryDirectory(prefix="oak-install-test-") as tmp:
        env = {**os.environ, "HOME": str(Path(tmp) / "home")}
        for harness in ("codex", "claude", "cursor", "chatgpt"):
            dest = Path(tmp) / harness
            dest.mkdir()
            (dest / "unrelated").mkdir()
            (dest / "unrelated/keep.txt").write_text("keep\n")
            command = ["bash", str(ROOT / "scripts/install-skills.sh"), "--harness", harness, str(dest)]
            install = lambda: subprocess.run(command, check=True, capture_output=True, input="\ny\n",
                                             text=True, env=env)
            install()
            stale = dest / next(iter(skills)) / "stale.txt"
            stale.write_text("obsolete\n")
            stale_agent = dest / "audit/references/specialists/obsolete.md"
            stale_agent.write_text("obsolete profile\n")
            install()
            require(not stale.exists(), f"{harness}: obsolete installed file survived")
            require(not stale_agent.exists(), f"{harness}: obsolete specialist survived")
            require((dest / "unrelated/keep.txt").read_text() == "keep\n", f"{harness}: unrelated directory changed")
            for name, directory in skills.items():
                require(packaged_inventory(directory) == inventory(dest / name), f"{harness}/{name}: installed bytes differ")
    print(f"PASS: {len(skills)} skill contracts, {len(corpus)} scenarios, 4 installation targets (including replacement).")
    print("Behavior and utility: not evaluated by this command.")


def prepare(case_id, destination, arm):
    case = next((c for c in cases() if c["id"] == case_id), None)
    require(case is not None, f"Unknown case: {case_id}")
    require(not destination.exists(), "Destination already exists; use a fresh directory")
    workspace = destination / "workspace"
    workspace.mkdir(parents=True)
    for name, content in case["files"].items():
        path = workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    # Supply the entire selected contract unchanged, without evaluator criteria.
    if arm == "skill":
        for harness_dir in (".agents/skills", ".claude/skills"):
            shutil.copytree(ROOT / "skills" / case["skill"], workspace / harness_dir / case["skill"])
            if case["skill"] == "audit":
                shutil.copytree(ROOT / "agents", workspace / harness_dir / "audit/references/specialists")
    request = case["prompt"]
    if arm == "skill":
        request = (f"Invoke {case['invocation']} using the project-local skill at "
                   f".agents/skills/{case['skill']}/SKILL.md. "
                   "Read that file before carrying out the request.\n\n" + request)
    (destination / "prompt.txt").write_text(request + "\n")
    (destination / "before.json").write_text(json.dumps(inventory(workspace), indent=2) + "\n")
    record = {
        "case": case_id, "arm": arm,
        "skill_source": packaged_inventory(ROOT / "skills" / case["skill"]),
        "model": None, "harness_version": None, "capabilities": None,
        "transcript": None, "elapsed_seconds": None, "clarification_count": None,
        "criteria": [{**criterion, "result": "not-run", "evidence": None} for criterion in case["checks"]],
        "value": case["value"], "notes": None,
    }
    (destination / "evaluation.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"Prepared {case_id} ({arm}): {workspace}")
    print("Keep evaluation.json and before.json outside the tested agent's context.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true")
    group.add_argument("--prepare", metavar="CASE")
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--arm", choices=("skill", "baseline"), default="skill")
    args = parser.parse_args()
    if args.prepare:
        if args.destination is None:
            parser.error("--prepare requires --destination")
        prepare(args.prepare, args.destination.resolve(), args.arm)
    elif args.list:
        for case in cases():
            print(f"{case['id']}: {case['invocation']}")
    else:
        check()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, yaml.YAMLError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"FAIL: {error}")
