"""Fail on npm audit advisories except the allowlisted GHSA IDs passed as arguments."""

import json
import sys

ignore = set(sys.argv[1:])
advisories = {}  # GHSA id -> (severity, title)
for package in json.load(sys.stdin).get("vulnerabilities", {}).values():
    for via in package["via"]:
        if isinstance(via, dict):  # a root advisory, not just an upstream package name
            advisories[via["url"].rsplit("/", 1)[-1]] = (via["severity"], via["title"])

remaining = {ghsa: info for ghsa, info in advisories.items() if ghsa not in ignore}
for ghsa, (severity, title) in sorted(remaining.items()):
    print(f"{severity}: {ghsa} {title}")
sys.exit(1 if remaining else 0)
