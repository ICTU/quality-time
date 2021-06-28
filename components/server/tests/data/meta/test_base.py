"""Unit tests for the base models."""

from data.meta.base import DescribedModel

from .base import MetaModelTestCase


class DescribedModelTest(MetaModelTestCase):
    """Data meta model unit tests."""

    MODEL = DescribedModel

    def test_description(self):
        """Test that a correct description passes the check and that a dot is added."""
        self.assertEqual(
            "Description.", DescribedModel.parse_obj(dict(name="Name", description="Description")).description
        )

    def test_missing_description(self):
        """Test that the description is mandatory."""
        self.check_validation_error("description\n  field required", name="Name")

    def test_empty_description(self):
        """Test that the description has a non-zero length."""
        self.check_validation_error('description\n  string does not match regex ".+"', name="Name", description="")
