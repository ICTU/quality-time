"""Unit tests for the database initialization."""

import unittest
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import mongomock

from shared.initialization.database import get_database, mongo_client

if TYPE_CHECKING:
    from pymongo import MongoClient


class TestConnectionParams(unittest.TestCase):
    """Test the database connection parameters."""

    def _assert_dbclient_host_url(self, client: MongoClient, expected_url: str) -> None:
        """Assert that the dbclient was initialized with expected url."""
        self.assertEqual(expected_url, client._init_kwargs["host"])  # noqa: SLF001

    def test_default(self):
        """Test the default url."""
        with mongo_client() as client:
            _default_user_pass = "root:root"  # nosec  # noqa: S105
            self._assert_dbclient_host_url(client, f"mongodb://{_default_user_pass}@localhost:27017")

    def test_full_url_override(self):
        """Test setting full url with env var override."""
        local_url = "mongodb://localhost"
        with patch.dict("os.environ", {"DATABASE_URL": local_url}), mongo_client() as client:
            self._assert_dbclient_host_url(client, local_url)

    def test_partial_url_override(self):
        """Test setting partial url with env var overrides."""
        env = {
            "DATABASE_USERNAME": "user",
            "DATABASE_PASSWORD": "pass",  # nosec
            "DATABASE_HOST": "host",
            "DATABASE_PORT": "4242",
        }
        with patch.dict("os.environ", env), mongo_client() as client:
            self._assert_dbclient_host_url(client, "mongodb://user:pass@host:4242")

    def test_read_username_and_password_from_file(self):
        """Test setting the credentials from file."""
        env = {
            "DATABASE_USERNAME_FILE": "user.txt",
            "DATABASE_PASSWORD_FILE": "password.txt",  # nosec
            "DATABASE_HOST": "host",
            "DATABASE_PORT": "4242",
        }
        with (
            patch.dict("os.environ", env),
            patch("shared.initialization.database.Path.read_text", Mock(side_effect=["user", "pass"])),
            mongo_client() as client,
        ):
            self._assert_dbclient_host_url(client, "mongodb://user:pass@host:4242")


class DatabaseInitTest(unittest.TestCase):
    """Unit tests for database initialization."""

    @patch("shared.initialization.database.pymongo", return_value=mongomock)
    def test_client(self, pymongo_mock: Mock) -> None:
        """Test that the client is called."""
        with mongo_client() as client:
            get_database(client)
        pymongo_mock.MongoClient.assert_called_once()
