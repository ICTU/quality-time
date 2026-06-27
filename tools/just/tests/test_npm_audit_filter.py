"""Unit tests for the npm audit filter."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from typing import TYPE_CHECKING, Any

from npm_audit_filter import audit_filter

if TYPE_CHECKING:
    from collections.abc import Iterable


def advisory(ghsa: str, severity: str = "high", title: str = "Title") -> dict[str, str]:
    """Create an npm audit advisory (the dict form of a 'via' entry)."""
    return {"url": f"https://github.com/advisories/{ghsa}", "severity": severity, "title": title}


def audit_json(*vias: Iterable[Any]) -> dict[str, Any]:
    """Create npm audit JSON with one vulnerability per passed list of 'via' entries."""
    return {"vulnerabilities": {f"package{index}": {"via": list(via)} for index, via in enumerate(vias)}}


class NpmAuditFilterTest(unittest.TestCase):
    """npm audit filter unit tests."""

    def filter(self, audit: dict[str, Any], ignore: Iterable[str] = ()) -> tuple[int, str]:
        """Run the audit filter and return the exit code and the captured output."""
        with redirect_stdout(io.StringIO()) as stdout:
            exit_code = audit_filter(audit, ignore)
        return exit_code, stdout.getvalue()

    def test_empty_json(self):
        """Test that an empty JSON is fine."""
        self.assertEqual((0, ""), self.filter({}))

    def test_no_vulnerabilities(self):
        """Test that a JSON without vulnerabilities is fine."""
        self.assertEqual((0, ""), self.filter({"vulnerabilities": {}}))

    def test_advisory(self):
        """Test that an advisory fails the filter and is printed."""
        self.assertEqual((1, "high: GHSA-1 Title\n"), self.filter(audit_json([advisory("GHSA-1")])))

    def test_ignored_advisory(self):
        """Test that an ignored advisory does not fail the filter and is not printed."""
        self.assertEqual((0, ""), self.filter(audit_json([advisory("GHSA-1")]), ["GHSA-1"]))

    def test_upstream_package_name_is_ignored(self):
        """Test that a 'via' that is a package name instead of an advisory is skipped."""
        self.assertEqual((0, ""), self.filter(audit_json(["upstream-package"])))

    def test_advisory_next_to_upstream_package_name(self):
        """Test that an advisory is reported even when it sits next to an upstream package name."""
        self.assertEqual((1, "high: GHSA-1 Title\n"), self.filter(audit_json([advisory("GHSA-1"), "upstream"])))

    def test_advisories_are_sorted(self):
        """Test that multiple advisories are printed sorted by GHSA id."""
        audit = audit_json([advisory("GHSA-2", "low", "Two")], [advisory("GHSA-1", "high", "One")])
        self.assertEqual((1, "high: GHSA-1 One\nlow: GHSA-2 Two\n"), self.filter(audit))

    def test_only_remaining_advisories_fail(self):
        """Test that ignoring some but not all advisories still fails for the remaining ones."""
        audit = audit_json([advisory("GHSA-1")], [advisory("GHSA-2")])
        self.assertEqual((1, "high: GHSA-2 Title\n"), self.filter(audit, ["GHSA-1"]))

    def test_duplicate_advisory_reported_once(self):
        """Test that the same advisory in multiple packages is reported only once."""
        audit = audit_json([advisory("GHSA-1")], [advisory("GHSA-1")])
        self.assertEqual((1, "high: GHSA-1 Title\n"), self.filter(audit))
