"""Unit tests for the datamodel routes."""

import http
from unittest.mock import patch

import bottle

from database.datamodels import default_metric_attributes, default_source_parameters, default_subject_attributes
from routes.datamodel import get_data_model
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
        mocked_request.headers = {"If-None-Match": "W/" + md5_hash("now")}
        try:
            get_data_model(self.database)
        except bottle.HTTPError as reason:
            self.assertEqual(http.HTTPStatus.NOT_MODIFIED, reason.status_code)

    def test_default_source_parameters(self):
        """Test that the default source parameters can be retrieved from the data model."""
        expected_parameters = {
            "landing_url": "",
            "password": "",
            "private_token": "",
            "severities": [],
            "url": "",
            "username": "",
        }
        self.assertEqual(expected_parameters, default_source_parameters(self.database, "security_warnings", "snyk"))

    def test_default_metric_attributes(self):
        """Test that the default metric attributes can be retrieved from the data model."""
        self.assertEqual(
            {
                "name": None,
                "type": "dependencies",
                "accept_debt": False,
                "addition": "sum",
                "debt_target": None,
                "direction": None,
                "near_target": "10",
                "target": "0",
                "scale": "count",
                "sources": {},
                "tags": ["maintainability"],
                "unit": None,
            },
            default_metric_attributes(self.database, "dependencies"),
        )

    def test_default_subject_attributes(self):
        """Test that the default subject attributes can be retrieved from the data model."""
        self.assertEqual(
            {
                "name": None,
                "description": "A custom software application or component.",
                "type": "software",
                "metrics": {},
            },
            default_subject_attributes(self.database, "software"),
        )
