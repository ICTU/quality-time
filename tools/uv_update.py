"""Work-around for the missing `uv update` command, see https://github.com/astral-sh/uv/issues/6794.

Limitations:
- This script only updates pyproject.toml, not uv.lock.
- This script only considers matching versions ("==") for upgrading.
- Version specs with other version clauses ("<=", "~=", etc.) are ignored.

This means that a version can be prevented from being updated, by using "package<=max version" as version spec.
"""

import pathlib
import re
import subprocess  # nosec


def replace_version(match: re.Match) -> str:
    """Replace the old version with the new version, if any."""
    name = match.group("name")
    version = new_versions.get(name.lower(), match.group("version"))
    return f'"{name}=={version}"'


uv_tree = ["uv", "tree", "--frozen", "--quiet", "--depth=1", "--outdated"]
outdated = subprocess.run(uv_tree, capture_output=True, text=True, check=True).stdout  # noqa: S603 # nosec
lines_with_updates = [line for line in outdated.splitlines() if " (latest: " in line]
new_versions = {line.split()[1]: line.split()[-1].lstrip("v").rstrip(")") for line in lines_with_updates}
package_spec = re.compile(r'"(?P<name>[A-Za-z0-9_.\-]+)==(?P<version>[A-Za-z0-9_.\-]+)"')
pyproject_toml = pathlib.Path("pyproject.toml")
pyproject_toml.write_text(package_spec.sub(replace_version, pyproject_toml.read_text()))
