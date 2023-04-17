"""Read the spec of a package from a pyproject.toml file."""

import sys
import tomllib
from pathlib import Path


def spec(package: str, pyproject_toml_path: Path) -> str:
    """Return the spec for the package from the pyproject.toml file."""
    with pyproject_toml_path.open("rb") as pyproject_toml_file:
        pyproject_toml = tomllib.load(pyproject_toml_file)
    tools = pyproject_toml["project"]["optional-dependencies"]["tools"]
    return [spec for spec in tools if spec.split("==")[0] == package][0]


if __name__ == "__main__":
    print(spec(sys.argv[1], Path("pyproject.toml")))
