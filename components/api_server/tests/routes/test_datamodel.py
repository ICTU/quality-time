"""Unit tests for the data model routes."""

import http
from unittest.mock import patch

import bottle

from routes import get_data_model
from utils.functions import md5_hash

from tests.base import DataModelTestCase


class DataModelTest(DataModelTestCase):
    """Unit tests for the data model route."""

    def test_get_data_model(self):
        """Test that the data model can be retrieved."""
        self.assertEqual(self.DATA_MODEL, get_data_model(self.database))

    def test_get_data_model_missing(self):
        """Test that the data model is None if it's not there."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, get_data_model(self.database))

    @patch("bottle.request")
    def test_get_data_model_unchanged(self, mocked_request):
        """Test that a 304 is returned when the data model is unchanged."""
        mocked_request.headers = {"If-None-Match": md5_hash("now")}
        try:
            get_data_model(self.database)
        except bottle.HTTPError as reason:
            self.assertEqual(http.HTTPStatus.NOT_MODIFIED, reason.status_code)
