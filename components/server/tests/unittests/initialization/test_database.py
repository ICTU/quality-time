"""Unit tests for the database initialization."""

import unittest
from unittest.mock import Mock, patch

import bottle

from src.initialization.database import init_database
from src.route_injection_plugin import InjectionPlugin


class DatabaseInitTest(unittest.TestCase):
    """Unit tests for database initialization."""

    def tearDown(self):
        bottle.app().uninstall(True)

    def test_init(self):
        """Test the initialization."""
        mock_mongo_client = Mock()
        database = Mock()
        database.datamodels.find_one.return_value = None
        database.database.reports.count_documents.return_value = 10
        database.database.measurements.count_documents.return_value = 20
        mock_mongo_client().quality_time_db = database
        with patch("pymongo.MongoClient", mock_mongo_client):
            init_database()
        self.assertEqual(InjectionPlugin, bottle.app().plugins[-1].__class__)
