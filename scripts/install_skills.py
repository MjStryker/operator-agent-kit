#!/usr/bin/env python3
"""Install, update, or restore OAK skills in harness skill directories.

Standard library only. Run it through scripts/install-skills.sh.
"""
import argparse
import datetime
import hashlib
import json
import os
import plistlib
import re
import secrets
import shutil
import stat
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SOURCE_ROOT = REPO_ROOT / "skills"
AGENTS_ROOT = REPO_ROOT / "agents"
COMPAT_FILE = SCRIPT_DIR / "install-compat.json"
HOME = Path(os.path.realpath(Path.home()))
DEFAULT_BACKUP_ROOT = HOME / ".oak/install/backups"

# Former OAK skill names and what replaced them. Detection relies on SKILL.md
# provenance; this table only adds a hint and flags unidentifiable remnants.
LEGACY_NAMES = {"take": "assess", "discover-complex-work": "recon"}

EXIT_OK, EXIT_CANCELLED, EXIT_USAGE, EXIT_PARTIAL, EXIT_FAILED = 0, 1, 2, 3, 4


class Refusal(Exception):
    """A request refused before any change."""


def codex_home():
    return Path(os.environ.get("CODEX_HOME") or HOME / ".codex")


def claude_home():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or HOME / ".claude")


def chatgpt_metadata():
    """Return (version, bundled codex path) of the ChatGPT desktop app, if found."""
    linux = Path("/usr/lib/chatgpt/resources")
    meta = linux / "linux-package-metadata.json"
    if meta.is_file():
        try:
            return json.loads(meta.read_text()).get("version"), linux / "codex"
        except (OSError, ValueError):
            return None, linux / "codex"
    plist = Path("/Applications/ChatGPT.app/Contents/Info.plist")
    if plist.is_file():
        try:
            with plist.open("rb") as handle:
                version = plistlib.load(handle).get("CFBundleShortVersionString")
        except (OSError, ValueError, plistlib.InvalidFileException):
            version = None
        return version, Path("/Applications/ChatGPT.app/Contents/Resources/codex")
    return None, None


def command_version(command):
    executable = shutil.which(command[0]) if os.sep not in command[0] else command[0]
    if not executable or not os.access(executable, os.X_OK):
        return None
    try:
        result = subprocess.run([executable, *command[1:]], capture_output=True, text=True,
                                timeout=10, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = (result.stdout or result.stderr).strip().splitlines()
    return lines[0].strip() if result.returncode == 0 and lines else None


def detect_version(harness):
    if harness == "chatgpt":
        version, bundled = chatgpt_metadata()
        if not version:
            return None
        codex = command_version([str(bundled), "--version"]) if bundled else None
        return f"{version} (bundled {codex})" if codex else version
    command = {"codex": ["codex", "--version"], "claude": ["claude", "--version"],
               "cursor": ["cursor", "--version"]}[harness]
    return command_version(command)


# Directories each harness reads for user-level skills, and the one OAK installs to.
def harness_table():
    agents = HOME / ".agents/skills"
    return {
        "codex": {"dest": agents, "reads": [agents, codex_home() / "skills"]},
        "chatgpt": {"dest": agents, "reads": [agents, codex_home() / "skills"]},
        "claude": {"dest": claude_home() / "skills", "reads": [claude_home() / "skills"]},
        "cursor": {"dest": HOME / ".cursor/skills",
                   "reads": [HOME / ".cursor/skills", agents, HOME / ".claude/skills",
                             HOME / ".codex/skills"]},
    }


KNOWN_HARNESSES = ("codex", "chatgpt", "claude", "cursor")
ALIASES = {"claude-code": "claude"}


def real(path):
    return Path(os.path.realpath(os.path.expanduser(str(path))))


def inside(path, parent):
    """True when path equals parent or lies below it."""
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def overlap(a, b):
    return inside(a, b) or inside(b, a)


def display(path):
    path = Path(path)
    return "~/" + str(path.relative_to(HOME)) if inside(path, HOME) and path != HOME else str(path)


# ---------------------------------------------------------------- provenance

def frontmatter(skill_md):
    """Minimal reader for name, metadata.repository and metadata.version."""
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return {}
    if not lines or lines[0].strip() != "---":
        return {}
    result, section = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip().strip('"').strip("'")
        if not line[0].isspace():
            section = key
            if key == "name":
                result["name"] = value
        elif section == "metadata" and key in ("repository", "version"):
            result[key] = value
    return result


def oak_repository():
    repositories = {frontmatter(path).get("repository") for path in SOURCE_ROOT.glob("*/SKILL.md")}
    if len(repositories) != 1 or not next(iter(repositories)):
        raise Refusal(f"Source skills do not declare one common metadata.repository: {sorted(map(str, repositories))}")
    return repositories.pop()


def classify(entry, repository):
    """Return ('oak', fm) or ('foreign', reason) for one skills-directory entry."""
    if entry.is_symlink():
        return "foreign", "symbolic link"
    if not entry.is_dir():
        return "foreign", "not a directory"
    fm = frontmatter(entry / "SKILL.md")
    if not fm:
        return "foreign", "no readable SKILL.md frontmatter"
    if fm.get("repository") != repository or fm.get("name") != entry.name:
        return "foreign", "SKILL.md does not identify it as OAK"
    return "oak", fm


# ---------------------------------------------------------------- inventories

def inventory(root):
    """Exact tree description: files (hash, mode), symlinks (target), directories."""
    result = {}
    root = Path(root)
    for current, dirs, files in os.walk(root, followlinks=False):
        current = Path(current)
        for name in sorted(dirs + files):
            path = current / name
            rel = str(path.relative_to(root))
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                result[rel] = ["link", os.readlink(path)]
            elif stat.S_ISDIR(info.st_mode):
                result[rel] = ["dir", stat.S_IMODE(info.st_mode)]
            elif stat.S_ISREG(info.st_mode):
                result[rel] = ["file", file_hash(path), stat.S_IMODE(info.st_mode)]
            else:
                result[rel] = ["special", stat.S_IFMT(info.st_mode)]
    return result


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def files_only(tree):
    return {rel: value[1] for rel, value in tree.items() if value[0] == "file"}


def subtree(tree, name):
    prefix = name + os.sep
    return {rel[len(prefix):]: value for rel, value in tree.items() if rel.startswith(prefix)}


def package_files(name):
    """Expected file hashes of one installed OAK skill."""
    expected = files_only(inventory(SOURCE_ROOT / name))
    if name == "audit":
        expected.update({f"references/specialists/{rel}": digest
                         for rel, digest in files_only(inventory(AGENTS_ROOT)).items()})
    return expected


def stage_package(name, destination):
    shutil.copytree(SOURCE_ROOT / name, destination, symlinks=True)
    if name == "audit":
        shutil.copytree(AGENTS_ROOT, destination / "references/specialists", symlinks=True,
                        dirs_exist_ok=True)
    if files_only(inventory(destination)) != package_files(name):
        raise OSError(f"staged copy of {name} differs from its source")


def move(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def remove(path):
    if path.is_symlink() or not path.is_dir():
        path.unlink()
    else:
        shutil.rmtree(path)


# ---------------------------------------------------------------- prompts

def ask(prompt):
    """Read one answer; None when no answer is available."""
    print(prompt, end="", flush=True)
    line = sys.stdin.readline()
    if not line:
        print()
        return None
    return line.strip()


def confirm(prompt, choices):
    answer = ask(prompt)
    answer = (answer or "").lower()
    return choices.get(answer)


# ---------------------------------------------------------------- planning

class Target:
    def __init__(self, dest, harnesses):
        self.dest = dest
        self.harnesses = harnesses
        self.label = "+".join(harnesses) if harnesses else "custom"
        self.ops = []        # (kind, name, detail)
        self.legacy = []     # (name, detail)
        self.alerts = []
        self.untouched = []

    @property
    def changes(self):
        return [op for op in self.ops if op[0] in ("new", "replace")]


def plan_target(target, repository, sources):
    dest = target.dest
    if dest.exists() and not dest.is_dir():
        raise Refusal(f"{dest} exists and is not a directory")
    entries = {entry.name: entry for entry in dest.iterdir()} if dest.is_dir() else {}
    for name in sources:
        version = frontmatter(SOURCE_ROOT / name / "SKILL.md").get("version", "?")
        if name not in entries:
            target.ops.append(("new", name, f"{version} (new)"))
            continue
        kind, info = classify(dest / name, repository)
        if kind != "oak":
            target.ops.append(("blocked", name, f"existing entry kept: {info}; OAK {name} {version} not installed"))
        elif files_only(inventory(dest / name)) == package_files(name):
            target.ops.append(("unchanged", name, version))
        else:
            old = info.get("version", "?")
            detail = f"{old} -> {version}" if old != version else f"{version} (installed files differ)"
            target.ops.append(("replace", name, detail))
    for name, entry in sorted(entries.items()):
        if name in sources:
            continue
        kind, info = classify(entry, repository)
        if kind == "oak":
            hint = f"replaced by {LEGACY_NAMES[name]}" if name in LEGACY_NAMES else "no longer in OAK"
            target.legacy.append((name, f"{info.get('version', '?')}, {hint}"))
        else:
            target.untouched.append(name)
            if name in LEGACY_NAMES:
                target.alerts.append(f"{name}: former OAK name, but provenance is not established ({info}); left intact")
    if not dest.exists():
        target.alerts.append(f"{display(dest)} does not exist and will be created")


def visibility_alerts(targets, selected, repository, sources, table):
    """Warn when a selected harness reads OAK skills from several directories."""
    alerts = []
    installed_dirs = {t.dest for t in targets}
    for harness in selected:
        holders, legacy = [], []
        for read_dir in dict.fromkeys(real(p) for p in table[harness]["reads"]):
            names = []
            if read_dir.is_dir():
                for entry in read_dir.iterdir():
                    if classify(entry, repository)[0] == "oak":
                        names.append(entry.name)
            if read_dir in installed_dirs or any(n in sources for n in names):
                holders.append(read_dir)
            if read_dir not in installed_dirs:
                legacy += [f"{n} in {display(read_dir)}" for n in names if n not in sources]
        if len(holders) > 1:
            alerts.append(f"{harness} reads OAK skills from several directories "
                          f"({', '.join(map(display, holders))}); duplicates may be listed")
        for item in legacy:
            alerts.append(f"{harness} also reads former OAK skill {item}; not cleaned (not an installation target)")
    return alerts


def compatibility(harness, version):
    try:
        data = json.loads(COMPAT_FILE.read_text())
    except (OSError, ValueError):
        data = {}
    entry = data.get("harnesses", {}).get(harness)
    if not version:
        return "version not detected; compatibility not verified"
    if not entry:
        return "compatibility not verified"
    if not re.search(rf"(?<![\d.]){re.escape(entry['version'])}(?![\d.])", version):
        return f"compatibility not verified for this version (evaluated: {entry['version']})"
    levels = "".join(f"\n      {level}: {entry.get(level, 'not verified')}"
                     for level in ("copy", "discovery", "invocation"))
    return f"evaluated in {data.get('evaluation', '?')}{levels}"


def check_destinations(targets):
    for target in targets:
        dest = target.dest
        if dest == Path("/") or inside(HOME, dest):
            raise Refusal(f"Refusing destination {dest}: it contains the home directory")
        for protected in (SOURCE_ROOT, AGENTS_ROOT):
            if overlap(dest, real(protected)):
                raise Refusal(f"Refusing destination {dest}: it overlaps OAK sources {protected}")
    for a in targets:
        for b in targets:
            if a is not b and overlap(a.dest, b.dest):
                raise Refusal(f"Refusing nested destinations {a.dest} and {b.dest}")


def check_backup_root(root, destinations, table):
    if root == Path("/"):
        raise Refusal("Refusing / as backup root")
    for dest in destinations:
        if overlap(root, dest):
            raise Refusal(f"Refusing backup root {root}: it overlaps skills directory {dest}")
    for harness in table.values():
        for read_dir in harness["reads"]:
            if inside(root, real(read_dir)):
                raise Refusal(f"Refusing backup root {root}: harnesses read skills from {read_dir}")
    if inside(root, real(REPO_ROOT)):
        raise Refusal(f"Refusing backup root {root}: it is inside the OAK source checkout")
    for ancestor in [root, *root.parents]:
        if ancestor.name == "skills" and ancestor.parent.name in (".agents", ".claude", ".cursor", ".codex"):
            raise Refusal(f"Refusing backup root {root}: it is inside skills directory {ancestor}")


# ---------------------------------------------------------------- backup

def source_commit():
    try:
        result = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def new_run_dir(root, kind):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / f"{stamp}-{kind}-{secrets.token_hex(3)}"


def backup(run_dir, kind, targets, extra):
    """Copy every target directory completely and verify the copy; return target records."""
    run_dir.mkdir(parents=True, exist_ok=False)
    records = []
    for target in targets:
        folder = run_dir / target.label
        folder.mkdir()
        record = {"label": target.label, "dest": str(target.dest), "harnesses": target.harnesses,
                  "existed": target.dest.is_dir()}
        if record["existed"]:
            shutil.copytree(target.dest, folder / "skills", symlinks=True)
            before = inventory(target.dest)
            if inventory(folder / "skills") != before:
                raise OSError(f"backup of {target.dest} does not match the original")
            (folder / "inventory.json").write_text(json.dumps(before, indent=1, sort_keys=True))
        (folder / "target.json").write_text(json.dumps(record, indent=2))
        records.append(record)
    manifest = {"kind": kind, "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source": str(REPO_ROOT), "commit": source_commit(), "targets": records, **extra}
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def update_manifest(run_dir, **fields):
    path = run_dir / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest.update(fields)
    path.write_text(json.dumps(manifest, indent=2))


def rollback(journal):
    errors = []
    for action, *paths in reversed(journal):
        try:
            if action == "placed":
                if os.path.lexists(paths[0]):
                    remove(paths[0])
            elif action == "moved":
                move(paths[1], paths[0])
            elif action == "created":
                paths[0].rmdir()
        except OSError as error:
            errors.append(f"{action} {paths}: {error}")
    return errors


def create_dirs(dest, journal):
    missing = []
    current = dest
    while not current.exists():
        missing.append(current)
        current = current.parent
    for path in reversed(missing):
        path.mkdir()
        journal.append(("created", path))


# ---------------------------------------------------------------- install

def select_harnesses(args):
    selected = []

    def add(value):
        for name in value.replace(",", " ").split():
            name = ALIASES.get(name, name)
            if name not in KNOWN_HARNESSES:
                raise Refusal(f"Unknown harness: {name} (known: {', '.join(KNOWN_HARNESSES)})")
            if name not in selected:
                selected.append(name)

    for value in args.harness or []:
        add(value)
    if args.all:
        add(" ".join(KNOWN_HARNESSES))
    if not selected and not args.dest:
        if not sys.stdin.isatty():
            raise Refusal("No harness selected. Use --harness, --all, or run interactively.")
        print("Available harnesses:")
        list_harnesses()
        answer = ask('\nSelect one or more by name (space/comma-separated, or "all"): ')
        if answer is None or not answer.strip():
            return None
        add(" ".join(KNOWN_HARNESSES) if answer.strip() == "all" else answer)
    return selected


def list_harnesses():
    table = harness_table()
    print(f"{'HARNESS':<10} {'INSTALLS TO':<28} ALSO READS")
    for name in KNOWN_HARNESSES:
        reads = [display(p) for p in table[name]["reads"] if p != table[name]["dest"]]
        print(f"{name:<10} {display(table[name]['dest']):<28} {', '.join(reads) or '-'}")


def build_targets(selected, dest_override, table):
    if dest_override and len(selected) > 1:
        raise Refusal("DEST can only be used with a single harness.")
    targets = {}
    if not selected:
        targets[real(dest_override)] = []
    for harness in selected:
        dest = real(dest_override) if dest_override else real(table[harness]["dest"])
        targets.setdefault(dest, []).append(harness)
    return [Target(dest, harnesses) for dest, harnesses in targets.items()]


def print_preview(targets, versions, run_dir, alerts):
    commit = source_commit()
    print(f"\nOAK source: {REPO_ROOT}" + (f" @ {commit[:12]}" if commit else ""))
    print(f"Backup run: {run_dir}")
    for target in targets:
        print(f"\n{display(target.dest)}  [{target.label}]")
        for harness in target.harnesses:
            print(f"  {harness} {versions[harness] or '(not detected)'}: {compatibility(harness, versions[harness])}")
        print(f"  Backup: {run_dir / target.label}" if target.dest.is_dir()
              else "  Backup: directory absent; its absence is recorded")
        for kind, name, detail in target.ops:
            print(f"  {kind.upper() if kind == 'blocked' else kind:<9} {name} {detail}")
        if target.legacy:
            print("  Former OAK skills (cleanup proposed, never automatic):")
            for name, detail in target.legacy:
                print(f"    {name} {detail}")
        if target.untouched:
            print(f"  Left intact: {', '.join(target.untouched)}")
        for alert in target.alerts:
            print(f"  ALERT: {alert}")
    for alert in alerts:
        print(f"ALERT: {alert}")


def install(args):
    table = harness_table()
    selected = select_harnesses(args)
    if selected is None:
        print("No harness selected; nothing was changed.")
        return EXIT_CANCELLED
    targets = build_targets(selected, args.dest, table)
    check_destinations(targets)
    repository = oak_repository()
    if (SOURCE_ROOT / "audit").is_dir() and not (AGENTS_ROOT / "common.md").is_file():
        raise Refusal(f"Missing reusable specialists: {AGENTS_ROOT}")
    sources = sorted(path.parent.name for path in SOURCE_ROOT.glob("*/SKILL.md"))

    default = args.backup_root or str(DEFAULT_BACKUP_ROOT)
    answer = ask(f"Backup root [{default}]: ")
    if answer is None:
        print("No answer; nothing was changed.")
        return EXIT_CANCELLED
    if not os.path.isabs(os.path.expanduser(answer or default)):
        raise Refusal(f"Refusing backup root {answer or default}: it must be an absolute path")
    root = real(answer or default)
    check_backup_root(root, [t.dest for t in targets], table)

    for target in targets:
        plan_target(target, repository, sources)
    versions = {harness: detect_version(harness) for harness in selected}
    alerts = visibility_alerts(targets, selected, repository, sources, table)
    run_dir = new_run_dir(root, "install")
    print_preview(targets, versions, run_dir, alerts)

    blocked = any(op[0] == "blocked" for t in targets for op in t.ops)
    has_legacy = any(t.legacy for t in targets)
    if not any(t.changes for t in targets) and not has_legacy:
        print("\nNothing to change; nothing was modified.")
        return EXIT_PARTIAL if blocked else EXIT_OK
    if has_legacy:
        choice = confirm("\nProceed? [y] install and remove the former OAK skills listed, "
                         "[i] install only, [N] cancel: ", {"y": "all", "yes": "all", "i": "install"})
    else:
        choice = confirm("\nApply these operations? [y/N] ", {"y": "install", "yes": "install"})
    if choice is None:
        print("Cancelled; nothing was changed.")
        return EXIT_CANCELLED
    if choice == "install" and not any(t.changes for t in targets):
        print("Nothing to install; nothing was changed.")
        return EXIT_PARTIAL if blocked else EXIT_OK

    try:
        backup(run_dir, "install", targets, {"selected": selected})
    except OSError as error:
        print(f"Backup failed: {error}\nNothing was changed. Incomplete backup left at {run_dir}.", file=sys.stderr)
        return EXIT_FAILED
    print(f"\nBackup complete: {run_dir}")

    work = run_dir / ".work"
    journal = []
    try:
        for target in targets:
            for kind, name, _ in target.changes:
                stage_package(name, work / "new" / target.label / name)
        for target in targets:
            create_dirs(target.dest, journal)
            for kind, name, _ in target.changes:
                if kind == "replace":
                    old = work / "old" / target.label / name
                    move(target.dest / name, old)
                    journal.append(("moved", target.dest / name, old))
                journal.append(("placed", target.dest / name))
                move(work / "new" / target.label / name, target.dest / name)
            if choice == "all":
                for name, _ in target.legacy:
                    old = work / "old" / target.label / name
                    move(target.dest / name, old)
                    journal.append(("moved", target.dest / name, old))
    except (OSError, KeyboardInterrupt) as error:
        problems = rollback(journal)
        update_manifest(run_dir, status="rolled-back" if not problems else "rollback-failed",
                        error=str(error))
        print(f"Installation failed: {error}", file=sys.stderr)
        if problems:
            print("Rollback incomplete:\n  " + "\n  ".join(problems), file=sys.stderr)
            print(f"Restore with: scripts/install-skills.sh --restore {run_dir}", file=sys.stderr)
        else:
            print("Every change was rolled back.", file=sys.stderr)
        return EXIT_FAILED

    status = verify_install(run_dir, targets, choice)
    shutil.rmtree(work, ignore_errors=True)
    update_manifest(run_dir, status="installed" if status == EXIT_OK else "installed-with-alerts",
                    cleanup=choice == "all")
    if status != EXIT_OK:
        print(f"Restore the previous state with: scripts/install-skills.sh --restore {run_dir}", file=sys.stderr)
        return status
    print(f"Done. Restore with: scripts/install-skills.sh --restore {run_dir}")
    return EXIT_PARTIAL if blocked else EXIT_OK


def verify_install(run_dir, targets, choice):
    status = EXIT_OK
    for target in targets:
        touched = {name for _, name, _ in target.changes}
        if choice == "all":
            touched |= {name for name, _ in target.legacy}
        for name in touched - {name for name, _ in target.legacy}:
            if files_only(inventory(target.dest / name)) != package_files(name):
                print(f"ERROR: {display(target.dest / name)} differs from the package", file=sys.stderr)
                status = EXIT_FAILED
        saved = run_dir / target.label / "inventory.json"
        before = json.loads(saved.read_text()) if saved.is_file() else {}
        after = inventory(target.dest)
        for name in set(rel.split(os.sep)[0] for rel in [*before, *after]) - touched:
            if subtree(before, name) != subtree(after, name) or before.get(name) != after.get(name):
                print(f"ERROR: {display(target.dest / name)} changed although it was not an OAK operation",
                      file=sys.stderr)
                status = EXIT_FAILED
        if status == EXIT_OK:
            print(f"Verified {target.label} -> {display(target.dest)}: "
                  f"{len(target.changes)} copied byte-identical, other entries unchanged")
    return status


# ---------------------------------------------------------------- restore

def load_run(run_dir):
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise Refusal(f"Not an OAK backup run: {run_dir}")
    manifest = json.loads(manifest_path.read_text())
    for record in manifest["targets"]:
        folder = run_dir / record["label"]
        if record["existed"]:
            saved = json.loads((folder / "inventory.json").read_text())
            if inventory(folder / "skills") != saved:
                raise Refusal(f"Backup {folder} is damaged; it no longer matches its inventory")
    return manifest


def restore(args):
    run_dir = real(args.restore)
    manifest = load_run(run_dir)
    table = harness_table()
    targets = [Target(Path(r["dest"]), r["harnesses"]) for r in manifest["targets"]]
    for target, record in zip(targets, manifest["targets"]):
        target.label = record["label"]
        target.record = record
    check_destinations(targets)
    root = run_dir.parent
    check_backup_root(root, [t.dest for t in targets], table)

    print(f"Restore from {run_dir} ({manifest['kind']}, {manifest['created']})")
    pending = False
    for target in targets:
        saved = (json.loads((run_dir / target.label / "inventory.json").read_text())
                 if target.record["existed"] else {})
        current = inventory(target.dest) if target.dest.is_dir() else {}
        names = sorted(set(rel.split(os.sep)[0] for rel in [*saved, *current]))
        print(f"\n{display(target.dest)}  [{target.label}]")
        if not target.record["existed"]:
            print("  directory did not exist at backup time; it will be removed")
        for name in names:
            was, now = subtree(saved, name), subtree(current, name)
            if name not in saved:
                print(f"  remove    {name}")
            elif name not in current:
                print(f"  recreate  {name}")
            elif was != now or saved[name] != current[name]:
                print(f"  restore   {name}")
            else:
                continue
            pending = True
    if not pending and all(t.record["existed"] == t.dest.is_dir() for t in targets):
        print("\nAlready identical to the backup; nothing was changed.")
        return EXIT_OK
    run = new_run_dir(root, "pre-restore")
    print(f"\nThe current state will first be backed up to {run}")
    if confirm("Restore? [y/N] ", {"y": True, "yes": True}) is None:
        print("Cancelled; nothing was changed.")
        return EXIT_CANCELLED
    try:
        backup(run, "pre-restore", targets, {"restoring": str(run_dir)})
    except OSError as error:
        print(f"Backup failed: {error}\nNothing was changed.", file=sys.stderr)
        return EXIT_FAILED

    work = run / ".work"
    journal = []
    try:
        for target in targets:
            if target.dest.is_dir():
                for entry in sorted(target.dest.iterdir()):
                    old = work / "old" / target.label / entry.name
                    move(entry, old)
                    journal.append(("moved", entry, old))
            if target.record["existed"]:
                create_dirs(target.dest, journal)
                for entry in sorted((run_dir / target.label / "skills").iterdir()):
                    journal.append(("placed", target.dest / entry.name))
                    if entry.is_dir() and not entry.is_symlink():
                        shutil.copytree(entry, target.dest / entry.name, symlinks=True)
                    else:
                        shutil.copy2(entry, target.dest / entry.name, follow_symlinks=False)
                shutil.copystat(run_dir / target.label / "skills", target.dest)
            elif target.dest.is_dir():
                target.dest.rmdir()
                journal.append(("removed-dir", target.dest))
    except (OSError, KeyboardInterrupt) as error:
        problems = rollback(journal)
        print(f"Restore failed: {error}", file=sys.stderr)
        print("Rollback incomplete:\n  " + "\n  ".join(problems) if problems
              else "Every change was rolled back.", file=sys.stderr)
        return EXIT_FAILED

    status = EXIT_OK
    for target in targets:
        if target.record["existed"]:
            saved = json.loads((run_dir / target.label / "inventory.json").read_text())
            if inventory(target.dest) != saved:
                print(f"ERROR: {display(target.dest)} does not match the backup", file=sys.stderr)
                status = EXIT_FAILED
        elif target.dest.exists():
            status = EXIT_FAILED
    shutil.rmtree(work, ignore_errors=True)
    update_manifest(run, status="restored" if status == EXIT_OK else "restore-unverified")
    if status == EXIT_OK:
        print(f"Restored and verified. The replaced state is kept in {run}")
    return status


def list_backups(args):
    root = real(args.backup_root or DEFAULT_BACKUP_ROOT)
    runs = sorted(root.glob("*/manifest.json")) if root.is_dir() else []
    if not runs:
        print(f"No backups in {root}")
    for path in runs:
        manifest = json.loads(path.read_text())
        targets = ", ".join(f"{r['label']}:{display(r['dest'])}" for r in manifest["targets"])
        print(f"{path.parent}  {manifest['kind']}  {manifest.get('status', 'backup-only')}  {targets}")
    return EXIT_OK


# ---------------------------------------------------------------- main

USAGE = """\
Install or update OAK skills for one or more harnesses.

  scripts/install-skills.sh
  scripts/install-skills.sh --harness NAME[,NAME...] [--backup-root DIR] [DEST]
  scripts/install-skills.sh --all [--backup-root DIR]
  scripts/install-skills.sh --list-harnesses
  scripts/install-skills.sh --list-backups [--backup-root DIR]
  scripts/install-skills.sh --restore RUN_DIR

Only skills whose SKILL.md identifies them as OAK are replaced. Any other entry
with an OAK skill name blocks that skill. Former OAK skills are listed and their
removal is offered, never automatic. Before any change, every affected skills
directory, including third-party skills, is fully backed up and verified.
The script always asks for the backup root (Enter keeps the default) and for
confirmation; refusing or giving no answer changes nothing.

DEST overrides the destination for a single harness, or installs to a custom
location when no harness is selected. Skill files are copied unchanged;
reusable specialists are bundled with audit.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(prog="install-skills.sh", description=USAGE,
                                     formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True)
    parser.add_argument("--harness", action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list-harnesses", action="store_true")
    parser.add_argument("--list-backups", action="store_true")
    parser.add_argument("--backup-root")
    parser.add_argument("--restore", metavar="RUN_DIR")
    parser.add_argument("--yes", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("dest", nargs="?")
    args = parser.parse_args(argv)
    try:
        if args.yes:
            raise Refusal("--yes was removed: the installer always asks for confirmation.")
        if args.list_harnesses:
            list_harnesses()
            return EXIT_OK
        if args.list_backups:
            return list_backups(args)
        if args.restore:
            return restore(args)
        return install(args)
    except Refusal as refusal:
        print(f"{refusal}\nNothing was changed.", file=sys.stderr)
        return EXIT_USAGE
    except KeyboardInterrupt:
        print("\nInterrupted before any change.", file=sys.stderr)
        return EXIT_CANCELLED
    except OSError as error:
        print(f"{error}\nStopped before any change.", file=sys.stderr)
        return EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
