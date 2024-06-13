"""Read the spec of a package from a pyproject.toml file."""

import sys
import tomllib
from pathlib import Path


def spec(package: str, pyproject_toml_path: Path) -> str:
    """Return the spec for the package from the tools section in the pyproject.toml file.

    Returns an empty string if no spec can be found for the specified package.
    """
    with pyproject_toml_path.open("rb") as pyproject_toml_file:
        pyproject_toml = tomllib.load(pyproject_toml_file)
    tools = pyproject_toml["project"]["optional-dependencies"]["tools"]
    package_specs = [spec for spec in tools if spec.split("==")[0] == package]
    return package_specs[0] if package_specs else ""


if __name__ == "__main__":
    print(spec(sys.argv[1], Path("pyproject.toml")))
