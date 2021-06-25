"""Tests for the generated documentation."""

import pathlib
import subprocess
import unittest

import git


class GeneratedDocumentationTest(unittest.TestCase):
    """Tests for the generated documentation."""

    def test_up_to_dateness(self):
        """Tests that the workspace is clean after generting the docs."""
        docs = pathlib.Path(__file__).resolve().parent.parent
        repo = git.Repo(docs.parent)
        create_metrics_and_sources = docs / "src" / "create_metrics_and_sources_md.py"
        subprocess.run(["python3", create_metrics_and_sources], check=True)  # skipcq: BAN-B603,BAN-B607
        metrics_and_sources = docs / "METRICS_AND_SOURCES.md"
        self.assertFalse(repo.is_dirty(path=metrics_and_sources))
