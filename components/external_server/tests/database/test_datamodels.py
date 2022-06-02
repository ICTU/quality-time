"""Unit tests for the database data models."""

import json
import unittest
from unittest.mock import Mock

from shared.data_model import DATA_MODEL_JSON

from database.datamodels import default_subject_attributes


class DefaultSubjectAttributesTest(unittest.TestCase):
    """Test the default subject attributes."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        data_model = json.loads(DATA_MODEL_JSON)
        data_model["_id"] = "id"
        self.database.datamodels.find_one.return_value = data_model

    def test_without_subject_type(self):
        """Test the default attriburws without specifying a subject type."""
        self.assertEqual(
            dict(type="ci", name=None, description="A continuous integration environment.", metrics={}),
            default_subject_attributes(self.database),
        )

    def test_with_subject_type(self):
        """Test the default attriburws without specifying a subject type."""
        self.assertEqual(
            dict(type="software", name=None, description="A custom software application or component.", metrics={}),
            default_subject_attributes(self.database, "software"),
        )
