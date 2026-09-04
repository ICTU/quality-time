"""Fail on npm audit advisories except the allowlisted GHSA IDs passed as arguments."""

import json
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


def advisories(audit_json: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Return the advisories in the npm audit JSON, mapping GHSA id to severity and title."""
    found: dict[str, tuple[str, str]] = {}
    for package in audit_json.get("vulnerabilities", {}).values():
        for via in package["via"]:
            if isinstance(via, dict):  # a root advisory, not just an upstream package name
                found[via["url"].rsplit("/", 1)[-1]] = (via["severity"], via["title"])
    return found


def audit_filter(audit_json: dict[str, Any], ignore: Iterable[str]) -> int:
    """Print the npm audit advisories that are not ignored and return the exit code."""
    ignored = set(ignore)
    remaining = {ghsa: info for ghsa, info in advisories(audit_json).items() if ghsa not in ignored}
    for ghsa, (severity, title) in sorted(remaining.items()):
        print(f"{severity}: {ghsa} {title}")  # noqa: T201
    return 1 if remaining else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(audit_filter(json.load(sys.stdin), sys.argv[1:]))
