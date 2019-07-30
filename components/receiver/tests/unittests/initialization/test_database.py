"""Unit tests for the database initialization."""

import unittest
from unittest.mock import Mock, patch

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

    def test_init_database(self):
        """Test the initialization of a database."""
        self.database.datamodels.find_one.return_value = None
        self.database.reports_overviews.find_one.return_value = None
        self.database.reports.count_documents.return_value = 0
        self.database.measurements.count_documents.return_value = 0
        with patch("pymongo.MongoClient", self.mongo_client):
            database = init_database()
        self.assertTrue(database)
