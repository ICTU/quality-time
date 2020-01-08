"""Unit tests for the datamodel routes."""

import unittest
from unittest.mock import Mock

from routes import datamodel
from database.datamodels import default_source_parameters, default_subject_attributes, insert_new_datamodel


class DataModelTest(unittest.TestCase):
    """Unit tests for the data model route."""

    def setUp(self):
        self.database = Mock()

    def test_get_data_model(self):
        """Test that the data model can be retrieved."""
        self.database.datamodels.find_one.return_value = dict(_id=123)
        self.assertEqual(dict(_id="123"), datamodel.get_datamodel(self.database))

    def test_get_data_model_missing(self):
        """Test that the data model is None if it's not there."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, datamodel.get_datamodel(self.database))

    def test_insert_data_model_with_id(self):
        """Test that a new data model can be inserted."""
        insert_new_datamodel(self.database, dict(_id="id"))
        self.database.datamodels.insert_one.assert_called_once()

    def test_insert_data_model_without_id(self):
        """Test that a new data model can be inserted."""
        insert_new_datamodel(self.database, dict())
        self.database.datamodels.insert_one.assert_called_once()

    def test_default_source_parameters(self):
        """Test that the default source parameters can be retrieved from the data model."""
        self.database.datamodels.find_one.return_value = dict(
            _id=123,
            sources=dict(
                source_type=dict(parameters=dict(
                    other_parameter=dict(metrics=[]),
                    parameter=dict(default_value="name", metrics=["metric_type"])))))
        self.assertEqual(dict(parameter="name"), default_source_parameters(self.database, "metric_type", "source_type"))

    def test_default_subject_attributes(self):
        """Test that the default subject attributes can be retrieved from the data model."""
        self.database.datamodels.find_one.return_value = dict(
            _id=123,
            subjects=dict(subject_type=dict(name="name", description="description")))
        self.assertEqual(
            dict(name=None, description="description", type="subject_type", metrics={}),
            default_subject_attributes(self.database, "subject_type"))
