"""Unit tests for the base models."""

import unittest

from shared_data_model.meta.base import DescribedModel, StrEnum

from .base import MetaModelTestCase


class DescribedModelTest(MetaModelTestCase):
    """Unit tests for described models."""

    MODEL = DescribedModel

    def test_description_without_punctuation(self):
        """Test that a description without punctuation fails."""
        self.check_validation_error(
            "The description of Name does not end with punctuation",
            name="Name",
            description="Description",
        )

    def test_description_with_punctuation(self):
        """Test that a description with punctuation passes the check."""
        self.assertEqual("Description?", DescribedModel(name="Name", description="Description?").description)

    def test_missing_description(self):
        """Test that the description is mandatory."""
        self.check_validation_error("description\n  Field required", name="Name")

    def test_empty_description(self):
        """Test that the description has a non-zero length."""
        self.check_validation_error("String should match pattern '.+'", name="Name", description="")


class StrEnumTest(unittest.TestCase):
    """Unit tests for the string enumeration class."""

    def test_format(self):
        """Test that the format method returns the value."""

        class FooEnum(StrEnum):
            """Concrete string enum."""

            FOO = "foo"

        self.assertEqual("foo", f"{FooEnum.FOO}")
