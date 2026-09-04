"""Fail on GHSA ids in the npm audit ignore list that none of the audited folders reports anymore.

The ignore list is shared by all folders with JavaScript dependencies, so an ignored advisory is only redundant when
none of those folders reports it. Hence this check audits all of them and compares the ignore list to the union.
"""

import json
import subprocess  # nosec B404 # Needed to run npm audit in each folder
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from npm_audit_filter import advisories

if TYPE_CHECKING:
    from collections.abc import Iterable


def redundant_ignores(audit_jsons: Iterable[dict[str, Any]], ignore: Iterable[str]) -> int:
    """Print the ignored GHSA ids that none of the npm audit JSONs reports and return the exit code."""
    reported = set[str]().union(*(advisories(audit_json).keys() for audit_json in audit_jsons))
    redundant = set(ignore) - reported
    for ghsa in sorted(redundant):
        print(f"redundant npm audit ignore: {ghsa}")  # noqa: T201
    return 1 if redundant else 0


def npm_audit(folder: Path) -> dict[str, Any]:
    """Run npm audit in the folder and return the parsed JSON.

    Npm audit exits non-zero when it finds vulnerabilities, so the exit code is ignored and the output is parsed
    instead. Npm reports its own failures, such as a missing lock file, as JSON with an error key instead of as
    unparsable output. Neither may be mistaken for 'no advisories', as that would make every ignore look redundant.
    """
    audit = subprocess.run(  # nosec B603 B607 # No untrusted input, and npm comes from the path as in the other checks
        ["npm", "audit", "--json"],  # noqa: S607 # Use npm from the path, as the other npm checks do
        capture_output=True,
        text=True,
        cwd=folder,
        check=False,
    )
    try:
        report = json.loads(audit.stdout)
    except json.JSONDecodeError:
        report = {"error": {"summary": audit.stderr.strip() or audit.stdout.strip()}}
    if "vulnerabilities" not in report:
        sys.exit(f"npm audit failed in {folder}: {report.get('error', {}).get('summary', 'unexpected audit output')}")
    return report


if __name__ == "__main__":  # pragma: no cover
    folders = [Path(folder) for folder in sys.argv[1].split()]
    sys.exit(redundant_ignores([npm_audit(folder) for folder in folders], sys.argv[2:]))
