"""Update all dependencies by running the individual updater scripts."""

import subprocess  # nosec B404
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SRC = Path(__file__).parent

# These scripts update different files, so they can run concurrently.
PARALLEL_SCRIPTS = (
    "dockerfile_base_image",
    "pyproject_toml",
    "github_action",
    "circle_ci_config",
    "manifest_images",
    "jsdelivr",
)
# node_engine and package_json both rewrite the package.json files, so they run sequentially (after the
# parallel scripts and after each other) to avoid concurrent writes to the same files.
SEQUENTIAL_SCRIPTS = ("node_engine", "package_json")


def run_script(name: str) -> int:
    """Run the updater script with the given name and return its exit code."""
    return subprocess.run([sys.executable, str(SRC / f"update_{name}.py")], check=False).returncode  # noqa: S603 # nosec: B603


def update_dependencies() -> int:
    """Run all updater scripts and return the highest exit code."""
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(run_script, PARALLEL_SCRIPTS))
    results.extend(run_script(name) for name in SEQUENTIAL_SCRIPTS)
    return max(results, default=0)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_dependencies())
