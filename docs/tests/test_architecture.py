"""Test the architecture of the component."""

import unittest

from archunitpython import assert_passes, project_files


class DependenciesTest(unittest.TestCase):
    """Unit test for module dependencies within the component."""

    @staticmethod
    def test_no_cyclic_dependencies():
        """Test that there are no cyclic dependencies."""
        assert_passes(project_files("src/").should().have_no_cycles())
