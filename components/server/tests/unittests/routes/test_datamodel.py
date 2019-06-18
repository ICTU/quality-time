"""Unit tests for the datamodel routes."""

import unittest
from unittest.mock import Mock

from src.routes import datamodel
from src.database.datamodels import default_source_parameters, default_subject_attributes, insert_new_datamodel


class DatamodelTest(unittest.TestCase):
    """Unit tests for the datamodel route."""
    def test_get_datamodel(self):
        """Test that the datamodel can be retrieved."""
        database = Mock()
        database.datamodels.find_one.return_value = dict(_id=123)
        self.assertEqual(dict(_id="123"), datamodel.get_datamodel(database))

    def test_get_datamodel_missing(self):
        """Test that the datamodel is None if it's not there."""
        database = Mock()
        database.datamodels.find_one.return_value = None
        self.assertEqual(None, datamodel.get_datamodel(database))

    def test_insert_datamodel_with_id(self):
        """Test that a new datamodel can be inserted."""
        database = Mock()
        insert_new_datamodel(database, dict(_id="id"))
        database.datamodels.insert_one.assert_called_once()

    def test_insert_datamodel_without_id(self):
        """Test that a new datamodel can be inserted."""
        database = Mock()
        insert_new_datamodel(database, dict())
        database.datamodels.insert_one.assert_called_once()

    def test_default_source_parameters(self):
        """Test that the default source parameters can be retrieved from the datamodel."""
        database = Mock()
        database.datamodels.find_one.return_value = dict(
            _id=123,
            sources=dict(
                source_type=dict(parameters=dict(
                    other_parameter=dict(metrics=[]),
                    parameter=dict(default_value="name", metrics=["metric_type"])))))
        self.assertEqual(dict(parameter="name"), default_source_parameters(database, "metric_type", "source_type"))

    def test_default_subject_attribures(self):
        """Test that the default subject attributes can be retrieved from the datamodel."""
        database = Mock()
        database.datamodels.find_one.return_value = dict(
            _id=123,
            subjects=dict(subject_type=dict(name="name", description="description")))
        self.assertEqual(
            dict(name="name", description="description", type="subject_type", metrics={}),
            default_subject_attributes(database, "subject_type"))
