"""Tests for the generated documentation."""

import pathlib
import subprocess
import unittest

import git


class GeneratedDocumentationTest(unittest.TestCase):
    """Tests for the generated documentation."""

    def test_up_to_dateness(self):
        """Tests that the workspace is clean after generating the docs."""
        docs = pathlib.Path(__file__).resolve().parent.parent
        repo = git.Repo(docs.parent)
        create_metrics_and_sources = docs / "src" / "create_metrics_and_sources_md.py"
        subprocess.run(["python3", create_metrics_and_sources], check=True)  # skipcq: BAN-B603,BAN-B607
        repo_is_clean = not repo.is_dirty(path=docs)
        dirty_files = [item.a_path for item in repo.index.diff(None)]
        self.assertTrue(repo_is_clean or ["docs/package-lock.json"] == dirty_files, dirty_files)
