"""Unit tests for the npm audit ignore check."""

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

from npm_ignore_check import npm_audit, redundant_ignores

from .test_npm_audit_filter import advisory, audit_json

if TYPE_CHECKING:
    from collections.abc import Iterable


class RedundantIgnoresTest(unittest.TestCase):
    """Npm audit ignore check unit tests."""

    def check(self, audits: Iterable[dict[str, Any]], ignore: Iterable[str] = ()) -> tuple[int, str]:
        """Run the check and return the exit code and the captured output."""
        with redirect_stdout(io.StringIO()) as stdout:
            exit_code = redundant_ignores(audits, ignore)
        return exit_code, stdout.getvalue()

    def message(self, *ghsas: str) -> str:
        """Create the expected output for the passed redundant GHSA ids."""
        return "".join(f"redundant npm audit ignore: {ghsa}\n" for ghsa in ghsas)

    def test_no_folders(self):
        """Test that an empty ignore list without folders to audit is fine."""
        self.assertEqual((0, ""), self.check([]))

    def test_no_ignores(self):
        """Test that an empty ignore list is fine, even when advisories are reported."""
        self.assertEqual((0, ""), self.check([audit_json([advisory("GHSA-1")])]))

    def test_reported_ignore(self):
        """Test that an ignored advisory that is still reported is not redundant."""
        self.assertEqual((0, ""), self.check([audit_json([advisory("GHSA-1")])], ["GHSA-1"]))

    def test_redundant_ignore(self):
        """Test that an ignored advisory that is no longer reported is redundant."""
        expected = self.message("GHSA-1")
        self.assertEqual((1, expected), self.check([audit_json()], ["GHSA-1"]))

    def test_ignore_reported_by_other_folder(self):
        """Test that an advisory reported by one folder is not redundant, even though the other folder is clean."""
        audits = [audit_json(), audit_json([advisory("GHSA-1")])]
        self.assertEqual((0, ""), self.check(audits, ["GHSA-1"]))

    def test_redundant_ignores_are_sorted(self):
        """Test that multiple redundant ignores are printed sorted by GHSA id."""
        expected = self.message("GHSA-1", "GHSA-2")
        self.assertEqual((1, expected), self.check([audit_json()], ["GHSA-2", "GHSA-1"]))

    def test_only_redundant_ignores_are_reported(self):
        """Test that a reported and an unreported ignore only report the unreported one."""
        audits = [audit_json([advisory("GHSA-1")])]
        expected = self.message("GHSA-2")
        self.assertEqual((1, expected), self.check(audits, ["GHSA-1", "GHSA-2"]))

    def test_upstream_package_name_is_ignored(self):
        """Test that a 'via' that is a package name instead of an advisory does not count as reported."""
        expected = self.message("GHSA-1")
        self.assertEqual((1, expected), self.check([audit_json(["upstream-package"])], ["GHSA-1"]))


class NpmAuditTest(unittest.TestCase):
    """Unit tests for running npm audit."""

    def run_npm_audit(self, stdout: str, stderr: str = "") -> dict[str, Any]:
        """Run npm audit with the subprocess output patched."""
        completed = Mock(stdout=stdout, stderr=stderr)
        with patch("subprocess.run", return_value=completed):
            return npm_audit(Path("components/frontend"))

    def test_audit_json_is_parsed(self):
        """Test that the npm audit JSON is parsed."""
        audit = audit_json([advisory("GHSA-1")])
        self.assertEqual(audit, self.run_npm_audit(json.dumps(audit)))

    def test_failing_audit_exits(self):
        """Test that an audit that produces no JSON exits with an error instead of reporting no advisories."""
        with self.assertRaises(SystemExit) as error:
            self.run_npm_audit("", "npm error code ENETUNREACH")
        self.assertIn("npm error code ENETUNREACH", str(error.exception))

    def test_failing_audit_without_stderr(self):
        """Test that the standard output is reported when a failing audit writes nothing to standard error."""
        with self.assertRaises(SystemExit) as error:
            self.run_npm_audit("not JSON")
        self.assertIn("not JSON", str(error.exception))

    def test_audit_error_as_json_exits(self):
        """Test that an audit that reports its own failure as JSON exits, instead of reporting no advisories."""
        no_lockfile = {"code": "ENOLOCK", "summary": "This command requires an existing lockfile."}
        error_json = json.dumps({"error": no_lockfile})
        with self.assertRaises(SystemExit) as error:
            self.run_npm_audit(error_json)
        self.assertIn("This command requires an existing lockfile.", str(error.exception))

    def test_unexpected_audit_json_exits(self):
        """Test that audit JSON with neither vulnerabilities nor an error exits."""
        with self.assertRaises(SystemExit) as error:
            self.run_npm_audit('{"metadata": {}}')
        self.assertIn("unexpected audit output", str(error.exception))
