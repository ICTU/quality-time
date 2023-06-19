"""Unit tests for the database initialization."""

from unittest.mock import Mock, patch

import mongomock

from shared.initialization.database import database_connection

from tests.shared.base import DataModelTestCase


class DatabaseInitTest(DataModelTestCase):
    """Unit tests for database initialization."""

    @patch("shared.initialization.database.pymongo", return_value=mongomock)
    def test_client(self, client: Mock) -> None:
        """Test that the client is called."""
        database_connection()
        client.MongoClient.assert_called_once()
