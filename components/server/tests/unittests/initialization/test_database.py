"""Unit tests for the database initialization."""

import unittest
from unittest.mock import Mock, mock_open, patch

import bottle

from src.initialization.database import init_database


class DatabaseInitTest(unittest.TestCase):
    """Unit tests for database initialization."""

    def setUp(self):
        self.mongo_client = Mock()
        self.database = Mock()
        self.mongo_client().quality_time_db = self.database

    def tearDown(self):
        bottle.app().uninstall(True)

    def test_init_empty_database(self):
        """Test the initialization of an empty database."""
        self.database.datamodels.find_one.return_value = None
        self.database.reports_overviews.find_one.return_value = None
        self.database.reports.count_documents.return_value = 0
        self.database.measurements.count_documents.return_value = 0
        datamodel_json = '{"change": "yes"}'
        with patch("pathlib.Path.glob", new=Mock(return_value=[])):
            with patch("builtins.open", mock_open(read_data=datamodel_json)):
                with patch("pymongo.MongoClient", self.mongo_client):
                    init_database()
        self.database.datamodels.insert_one.assert_called_once()
        self.database.reports_overviews.insert.assert_called_once()

    def test_init_initialized_database(self):
        """Test the initialization of an initialized database."""
        self.database.datamodels.find_one.return_value = dict(_id="id", timestamp="now")
        self.database.reports_overviews.find_one.return_value = dict(_id="id")
        self.database.reports.count_documents.return_value = 10
        self.database.measurements.count_documents.return_value = 20
        datamodel_json = '{}'
        with patch("pathlib.Path.glob", new=Mock(return_value=[])):
            with patch("builtins.open", mock_open(read_data=datamodel_json)):
                with patch("pymongo.MongoClient", self.mongo_client):
                    init_database()
        self.database.datamodels.insert_one.assert_not_called()
        self.database.reports_overviews.insert.assert_not_called()
