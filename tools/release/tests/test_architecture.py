"""Test the architecture of the tool."""

import unittest

from archunitpython import assert_passes, project_files


class DependenciesTest(unittest.TestCase):
    """Unit test for module dependencies within the tool.

    A test for no cyclic dependencies is missing because the two Python files don't import each other, making
    `project_files("src/").should().have_no_cycles()` fail with 'No files found matching the specified patterns'.
    """

    def test_no_script_imports(self):
        """Test that scripts are not imported."""
        assert_passes(project_files("src/").should_not().depend_on_files().with_name("release.py"))
