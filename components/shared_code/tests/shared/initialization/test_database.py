"""Unit tests for the database initialization."""

import os
from unittest.mock import Mock, patch

import mongomock

from shared.initialization.database import database_connection

from tests.shared.base import DataModelTestCase
from tests.shared_test_utils import disable_logging


@patch("shared.initialization.database.pymongo", return_value=mongomock)
class DatabaseInitTest(DataModelTestCase):
    """Unit tests for database initialization."""

    @patch.dict(
        os.environ,
        {"DATABASE_HOST": "database", "DATABASE_PORT": "99", "DATABASE_USER": "user", "DATABASE_PASSWORD": "pass"},
    )
    def test_init_with_database_parameters(self, client: Mock) -> None:
        """Test that the client is called."""
        database_connection()
        client.MongoClient.assert_called_once_with("mongodb://user:pass@database:99")

    @disable_logging
    @patch.dict(os.environ, {"DATABASE_URL": "mongodb://database"})
    def test_init_with_deprecated_database_url(self, client: Mock) -> None:
        """Test that the client is called with the database URL, if provided."""
        database_connection()
        client.MongoClient.assert_called_once_with("mongodb://database")
