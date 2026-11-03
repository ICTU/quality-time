"""Unit tests for the data model routes."""

import http
from unittest.mock import patch

import bottle

from shared.utils.functions import md5_hash
from shared_data_model.meta.config import Config

from routes import get_data_model
from routes.datamodel import CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG

from tests.base import DatabaseWithDataModelTestCase


class DataModelTest(DatabaseWithDataModelTestCase):
    """Unit tests for the data model route."""

    def test_get_data_model(self):
        """Test that the data model can be retrieved."""
        self.assertEqual(self.DATA_MODEL, get_data_model(self.database))

    def test_get_data_model_without_config(self):
        """Test that the configuration of data models without configuration is added to data models without it."""
        old_data_model = self.DATA_MODEL.copy()
        del old_data_model["config"]
        self.database.datamodels.find_one.return_value = old_data_model
        data_model = get_data_model(self.database)
        self.assertEqual(CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG, data_model["config"])

    def test_get_data_model_with_config(self):
        """Test that the configuration of data models that have one is not changed."""
        data_model = self.DATA_MODEL.copy()
        data_model["config"] = {"desired_response_times": {"unknown": 1}}
        self.database.datamodels.find_one.return_value = data_model
        self.assertEqual({"desired_response_times": {"unknown": 1}}, get_data_model(self.database)["config"])

    def test_get_data_model_with_incomplete_config(self):
        """Test that missing configuration settings are added to data models that don't have them."""
        old_data_model = self.DATA_MODEL.copy()
        old_data_model["config"] = {}
        self.database.datamodels.find_one.return_value = old_data_model
        data_model = get_data_model(self.database)
        self.assertEqual(
            CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG["desired_response_times"],
            data_model["config"]["desired_response_times"],
        )

    def test_config_of_data_models_without_config_is_valid(self):
        """Test that the configuration of data models without configuration is a valid configuration."""
        self.assertEqual(
            CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG,
            Config.model_validate(CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG).model_dump(),
        )

    def test_get_data_model_missing(self):
        """Test that the data model is None if it's not there."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, get_data_model(self.database))

    @patch("bottle.request")
    def test_get_data_model_unchanged(self, mocked_request):
        """Test that a 304 is returned when the data model is unchanged."""
        get_data_model(self.database)
        mocked_request.headers = {"If-None-Match": bottle.response.get_header("ETag")}
        with self.assertRaises(bottle.HTTPError) as context:
            get_data_model(self.database)
        self.assertEqual(http.HTTPStatus.NOT_MODIFIED, context.exception.status_code)

    @patch("bottle.request")
    def test_get_data_model_cached_before_config_was_inserted(self, mocked_request):
        """Test that the data model is returned if the client cached it before the config was inserted."""
        mocked_request.headers = {"If-None-Match": md5_hash("now")}  # The ETag used to be the hash of the timestamp
        self.assertEqual(self.DATA_MODEL, get_data_model(self.database))
