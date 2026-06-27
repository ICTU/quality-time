"""Fail on npm audit advisories except the allowlisted GHSA IDs passed as arguments."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


def audit_filter(audit_json: dict[str, Any], ignore: Iterable[str]) -> int:
    """Print the npm audit advisories that are not ignored and return the exit code."""
    ignored = set(ignore)
    advisories: dict[str, tuple[str, str]] = {}  # GHSA id -> (severity, title)
    for package in audit_json.get("vulnerabilities", {}).values():
        for via in package["via"]:
            if isinstance(via, dict):  # a root advisory, not just an upstream package name
                advisories[via["url"].rsplit("/", 1)[-1]] = (via["severity"], via["title"])

    remaining = {ghsa: info for ghsa, info in advisories.items() if ghsa not in ignored}
    for ghsa, (severity, title) in sorted(remaining.items()):
        print(f"{severity}: {ghsa} {title}")  # noqa: T201
    return 1 if remaining else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(audit_filter(json.load(sys.stdin), sys.argv[1:]))
