#!/usr/bin/env python3
"""Look for private data in tracked or staged files before publishing.

Generic patterns: email addresses (GitHub noreply and example domains allowed),
personal home directory paths, and common credential formats. Optional private
terms, such as company or colleague names, are read from a local file kept
outside the repository: $OAK_PRIVATE_TERMS, or ~/.config/oak/private-terms.txt.
One term per line; blank lines and lines starting with # are ignored; matching
ignores case.

This catches common mistakes; it does not prove a file is free of private data.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})")
ALLOWED_EMAIL_DOMAINS = ("users.noreply.github.com", "example.com", "example.org", "example.net")
PATTERNS = {
    "home directory path": re.compile(r"/home/[a-z_][\w.-]*|/Users/[A-Za-z][\w.-]*|[A-Za-z]:\\Users\\[A-Za-z]"),
    "credential": re.compile(
        r"(?<![\w-])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_\w{30,}|glpat-[\w-]{20,}"
        r"|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})|-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def private_terms():
    path = Path(os.environ.get("OAK_PRIVATE_TERMS") or Path.home() / ".config/oak/private-terms.txt")
    if not path.is_file():
        return []
    lines = (line.strip() for line in path.read_text().splitlines())
    return [line.lower() for line in lines if line and not line.startswith("#")]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True).stdout


def files(staged):
    if staged:
        names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").decode().split("\0")
        return [(name, lambda n=name: git("show", f":{n}")) for name in names if name]
    names = git("ls-files", "-z").decode().split("\0")
    return [(name, lambda n=name: (ROOT / n).read_bytes()) for name in names if name and (ROOT / name).is_file()]


def scan(text, terms):
    for number, line in enumerate(text.splitlines(), 1):
        for match in EMAIL.finditer(line):
            if match.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
                yield number, "email address"
        for kind, pattern in PATTERNS.items():
            if pattern.search(line):
                yield number, kind
        lowered = line.lower()
        if any(term in lowered for term in terms):
            yield number, "private term"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--staged", action="store_true", help="check staged content instead of tracked files")
    args = parser.parse_args()
    terms = private_terms()
    found = 0
    for name, read in files(args.staged):
        try:
            text = read().decode()
        except UnicodeDecodeError:
            continue
        for number, kind in scan(text, terms):
            print(f"{name}:{number}: {kind}")
            found += 1
    if found:
        print(f"FAIL: {found} possible private data match(es). Remove them, or use invented generic values.")
        return 1
    source = "with local private terms" if terms else "no local private terms file"
    print(f"PASS: no private data pattern found ({source}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
