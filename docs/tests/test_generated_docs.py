"""Tests for the generated documentation."""

import pathlib
import unittest

import git

from create_metrics_and_sources_md import main


class GeneratedDocumentationTest(unittest.TestCase):
    """Tests for the generated documentation."""

    def test_up_to_dateness(self):
        """Tests that the workspace is clean after generating the docs."""
        docs = pathlib.Path(__file__).resolve().parent.parent
        repo = git.Repo(docs.parent)
        main()
        repo_is_clean = not repo.is_dirty(path=docs)
        dirty_files = [item.a_path for item in repo.index.diff(None)]
        self.assertTrue(repo_is_clean or ["docs/package-lock.json"] == dirty_files, dirty_files)
