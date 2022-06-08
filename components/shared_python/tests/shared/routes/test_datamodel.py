"""Unit tests for the datamodel routes."""

import unittest
from unittest.mock import Mock, patch

import bottle

from shared.utils.functions import md5_hash
from shared.routes import get_data_model


class DataModelTest(unittest.TestCase):
    """Unit tests for the data model route."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()

    def test_get_data_model(self):
        """Test that the data model can be retrieved."""
        data_model = self.database.datamodels.find_one.return_value = dict(_id=123, timestamp="now")
        self.assertEqual(data_model, get_data_model(self.database))

    def test_get_data_model_missing(self):
        """Test that the data model is None if it's not there."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, get_data_model(self.database))

    @patch("bottle.request")
    def test_get_data_model_unchanged(self, mocked_request):
        """Test that a 304 is returned when the data model is unchanged."""
        mocked_request.headers = {"If-None-Match": "W/" + md5_hash("now")}
        self.database.datamodels.find_one.return_value = dict(_id=123, timestamp="now")
        self.assertRaises(bottle.HTTPError, get_data_model, self.database)
