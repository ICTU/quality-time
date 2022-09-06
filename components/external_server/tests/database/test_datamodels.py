"""Unit tests for the database data models."""

from database.datamodels import default_subject_attributes

from ..base import DataModelTestCase


class DefaultSubjectAttributesTest(DataModelTestCase):
    """Test the default subject attributes."""

    def test_default_attributes(self):
        """Test the default attributes for a specific subject type."""
        self.assertEqual(
            dict(type="software", name=None, description="A custom software application or component.", metrics={}),
            default_subject_attributes(self.database, "software"),
        )
