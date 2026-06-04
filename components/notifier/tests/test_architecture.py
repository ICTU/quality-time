"""Test the architecture of the component."""

import unittest

from archunitpython import assert_passes, project_files

from shared_test_code import package_names, path_glob


class DependenciesTest(unittest.TestCase):
    """Unit test for module dependencies within the component."""

    SOURCE_PACKAGES = package_names("src")

    def test_no_cyclic_dependencies(self):
        """Test that there are no cyclic dependencies."""
        assert_passes(project_files("src/").should().have_no_cycles())

    def test_notifier_utilities_is_the_foundation_layer(self):
        """Test that notifier_utilities is a leaf that does not depend on other internal packages."""
        utilities = project_files("src/").in_path(path_glob("src/notifier_utilities"))
        for package in self.SOURCE_PACKAGES:
            if package != "notifier_utilities":
                assert_passes(utilities.should_not().depend_on_files().in_path(path_glob(f"src/{package}")))
