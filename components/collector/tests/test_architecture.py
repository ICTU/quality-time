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

    def test_collector_utilities_is_the_foundation_layer(self):
        """Test that collector_utilities is a leaf that does not depend on other internal packages."""
        utilities = project_files("src/").in_path(path_glob("src/collector_utilities"))
        for package in self.SOURCE_PACKAGES:
            if package != "collector_utilities":
                assert_passes(utilities.should_not().depend_on_files().in_path(path_glob(f"src/{package}")))

    def test_domain_model_does_not_depend_on_collection_logic(self):
        """Test that the model package holds domain types only, free of collector and database code."""
        model = project_files("src/").in_path(path_glob("src/model"))
        for package in self.SOURCE_PACKAGES:
            if package not in ("model", "collector_utilities"):  # The model may use collector_utilities
                assert_passes(model.should_not().depend_on_files().in_path(path_glob(f"src/{package}")))

    def test_base_collectors_do_not_import_concrete_source_collectors(self):
        """Test that the framework discovers source collectors dynamically instead of importing them."""
        base_collectors = project_files("src/").in_path(path_glob("src/base_collectors"))
        assert_passes(base_collectors.should_not().depend_on_files().in_path(path_glob("src/source_collectors")))
