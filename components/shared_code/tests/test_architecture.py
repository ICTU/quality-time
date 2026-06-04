"""Test the architecture of the component."""

import unittest

from archunitpython import CheckOptions, assert_passes, project_files

from shared_test_code import package_names, path_glob


class DependenciesTest(unittest.TestCase):
    """Unit test for module dependencies within the component."""

    SHARED_SOURCE_PACKAGES = package_names("src/shared")
    SHARED_DATA_MODEL_PACKAGES = package_names("src/shared_data_model")

    def test_no_cyclic_dependencies(self):
        """Test that there are no cyclic dependencies."""
        assert_passes(project_files("src/").should().have_no_cycles(), CheckOptions(ignore_type_checking_imports=True))

    def test_utilities_is_the_foundation_layer(self):
        """Test that utilities do not depend on other internal packages."""
        utilities = project_files("src/").in_path(path_glob("src/shared/utils"))
        for package in self.SHARED_SOURCE_PACKAGES:
            if package != "utils":
                assert_passes(utilities.should_not().depend_on_files().in_path(path_glob(f"src/shared/{package}")))
        for package in self.SHARED_DATA_MODEL_PACKAGES:
            assert_passes(
                utilities.should_not().depend_on_files().in_path(path_glob(f"src/shared_data_model/{package}"))
            )

    def test_shared_data_model_meta_(self):
        """Test that the meta model does not depend on other internal packages."""
        meta = project_files("src/").in_path(path_glob("src/shared_data_model/meta"))
        for package in self.SHARED_SOURCE_PACKAGES:
            if package != "utils":
                assert_passes(meta.should_not().depend_on_files().in_path(path_glob(f"src/shared/{package}")))
        for package in self.SHARED_DATA_MODEL_PACKAGES:
            if package not in ("meta", "logos"):  # The meta model checks that every source has a logo
                assert_passes(
                    meta.should_not().depend_on_files().in_path(path_glob(f"src/shared_data_model/{package}"))
                )
