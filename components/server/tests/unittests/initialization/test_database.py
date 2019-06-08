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
        quality_time_db = Mock()
        quality_time_db.datamodels.find_one.return_value = None
        mock_mongo_client().quality_time_db = quality_time_db
        with patch("pymongo.MongoClient", mock_mongo_client):
            init_database()
        self.assertEqual(InjectionPlugin, bottle.app().plugins[-1].__class__)
