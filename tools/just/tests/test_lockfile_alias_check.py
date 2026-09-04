"""Unit tests for the lockfile alias check."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

from lockfile_alias_check import lockfile_path, read_json, redundant_aliases

if TYPE_CHECKING:
    from collections.abc import Iterable


def config_json(*aliases: str) -> dict[str, Any]:
    """Create a lockfile-lint config with the passed allowed package name aliases."""
    return {"path": "package-lock.json", "allowed-package-name-aliases": list(aliases)}


def lockfile_json(*packages: tuple[str, str]) -> dict[str, Any]:
    """Create lock file JSON with a root package and one entry per passed (path, name) pair."""
    entries = {path: {"name": name, "version": "1.0.0"} for path, name in packages}
    return {"packages": {"": {"name": "root-package"}} | entries}


class LockfileAliasCheckTest(unittest.TestCase):
    """Lockfile alias check unit tests."""

    def check(self, config: dict[str, Any], lockfile: dict[str, Any]) -> tuple[int, str]:
        """Run the check and return the exit code and the captured output."""
        with redirect_stdout(io.StringIO()) as stdout:
            exit_code = redundant_aliases(config, lockfile)
        return exit_code, stdout.getvalue()

    def message(self, *aliases: Iterable[str]) -> str:
        """Create the expected output for the passed redundant aliases."""
        return "".join(f"redundant allowed package name alias: {alias}\n" for alias in aliases)

    def test_empty_json(self):
        """Test that empty JSON is fine."""
        self.assertEqual((0, ""), self.check({}, {}))

    def test_no_allowed_aliases(self):
        """Test that a config without allowed aliases is fine."""
        self.assertEqual((0, ""), self.check(config_json(), lockfile_json()))

    def test_used_alias(self):
        """Test that an allowed alias that the lock file uses is not reported."""
        lockfile = lockfile_json(("node_modules/react-is-18", "react-is"))
        self.assertEqual((0, ""), self.check(config_json("react-is-18:react-is"), lockfile))

    def test_unused_alias(self):
        """Test that an allowed alias that the lock file does not use is reported."""
        expected = self.message("react-is-18:react-is")
        self.assertEqual((1, expected), self.check(config_json("react-is-18:react-is"), lockfile_json()))

    def test_scoped_alias(self):
        """Test that a scoped alias is matched by its full name, including the scope."""
        lockfile = lockfile_json(("node_modules/@jest/react-is-18", "react-is"))
        self.assertEqual((0, ""), self.check(config_json("@jest/react-is-18:react-is"), lockfile))

    def test_renamed_scope(self):
        """Test that an alias is reported when the lock file moved it to a scope."""
        lockfile = lockfile_json(("node_modules/@jest/react-is-18", "react-is"))
        expected = self.message("react-is-18:react-is")
        self.assertEqual((1, expected), self.check(config_json("react-is-18:react-is"), lockfile))

    def test_nested_alias(self):
        """Test that an alias nested in the dependencies of another package is found."""
        lockfile = lockfile_json(("node_modules/jest/node_modules/react-is-18", "react-is"))
        self.assertEqual((0, ""), self.check(config_json("react-is-18:react-is"), lockfile))

    def test_alias_to_other_package(self):
        """Test that an allowed alias pointing to another package than the lock file uses is reported."""
        lockfile = lockfile_json(("node_modules/react-is-18", "react-is"))
        expected = self.message("react-is-18:evil-package")
        self.assertEqual((1, expected), self.check(config_json("react-is-18:evil-package"), lockfile))

    def test_package_without_name(self):
        """Test that a package without a name, the usual case, is not an alias."""
        lockfile = {"packages": {"node_modules/react-is": {"version": "18.3.1"}}}
        expected = self.message("react-is-18:react-is")
        self.assertEqual((1, expected), self.check(config_json("react-is-18:react-is"), lockfile))

    def test_workspace_is_not_an_alias(self):
        """Test that a workspace, whose name differs from its path, is not mistaken for an alias."""
        lockfile = lockfile_json(("components/frontend", "quality-time-app"))
        self.assertEqual((0, ""), self.check(config_json(), lockfile))

    def test_redundant_aliases_are_sorted(self):
        """Test that multiple redundant aliases are printed sorted by alias."""
        config = config_json("react-is-19:react-is", "react-is-18:react-is")
        expected = self.message("react-is-18:react-is", "react-is-19:react-is")
        self.assertEqual((1, expected), self.check(config, lockfile_json()))

    def test_only_redundant_aliases_are_reported(self):
        """Test that a used and an unused alias in the same config only report the unused one."""
        config = config_json("react-is-18:react-is", "react-is-19:react-is")
        lockfile = lockfile_json(("node_modules/react-is-18", "react-is"))
        expected = self.message("react-is-19:react-is")
        self.assertEqual((1, expected), self.check(config, lockfile))


@patch("pathlib.Path.read_text")
@patch("pathlib.Path.exists")
class ReadJSONTest(unittest.TestCase):
    """Unit tests for reading the config and lock file."""

    def test_existing_file(self, mock_exists: Mock, mock_read_text: Mock):
        """Test that an existing JSON file is parsed."""
        mock_exists.return_value = True
        mock_read_text.return_value = '{"packages": {}}'
        self.assertEqual({"packages": {}}, read_json(Path("package-lock.json")))

    def test_missing_file(self, mock_exists: Mock, mock_read_text: Mock):
        """Test that a missing JSON file, for example a folder without lockfile-lint config, is empty."""
        mock_exists.return_value = False
        self.assertEqual({}, read_json(Path("package-lock.json")))
        mock_read_text.assert_not_called()


class LockfilePathTest(unittest.TestCase):
    """Unit tests for determining the lock file to read."""

    def test_default_path(self):
        """Test that the lock file defaults to the package-lock.json next to the config."""
        self.assertEqual(Path.cwd() / "package-lock.json", lockfile_path({}, Path()))

    def test_configured_path(self):
        """Test that the lock file configured in the config is used."""
        config = {"path": "npm-shrinkwrap.json"}
        self.assertEqual(Path.cwd() / "npm-shrinkwrap.json", lockfile_path(config, Path()))

    def test_path_outside_folder(self):
        """Test that a lock file path that points outside the folder of the config is refused."""
        config = {"path": "../../../etc/passwd"}
        with self.assertRaises(SystemExit) as error:
            lockfile_path(config, Path())
        self.assertIn("points outside", str(error.exception))
