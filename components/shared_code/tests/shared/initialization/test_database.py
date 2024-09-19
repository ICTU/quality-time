"""Unit tests for the database initialization."""

from unittest.mock import Mock, patch

import mongomock

from shared.initialization.database import get_database, mongo_client

from tests.shared.base import DataModelTestCase


class DatabaseInitTest(DataModelTestCase):
    """Unit tests for database initialization."""

    @patch("shared.initialization.database.pymongo", return_value=mongomock)
    def test_get_database(self, pymongo_client: Mock) -> None:
        """Test that the client is called."""
        with mongo_client() as client:
            get_database(client)
        pymongo_client.MongoClient.assert_called_once()
