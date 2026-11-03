#!/usr/bin/env bash
# Entry point for the OAK skill installer; see scripts/install_skills.py.
set -euo pipefail
exec python3 "$(dirname -- "${BASH_SOURCE[0]}")/install_skills.py" "$@"
