"""Test the database connection parameters."""

import unittest
from unittest.mock import Mock, patch

import pymongo

from shared.initialization.database import mongo_client

OS_ENVIRON_GET = "shared.initialization.database.os.environ.get"


class TestConnectionParams(unittest.TestCase):
    """Test the database connection parameters."""

    def assert_mongo_client_host_url(self, client: pymongo.MongoClient, expected_url: str) -> None:
        """Assert that the dbclient was initialized with expected url."""
        self.assertEqual(expected_url, client._init_kwargs["host"])  # noqa: SLF001

    def test_default(self):
        """Test the default url."""
        _default_user_pass = "root:root"  # nosec  # noqa: S105
        with mongo_client() as client:
            self.assert_mongo_client_host_url(client, f"mongodb://{_default_user_pass}@localhost:27017")

    def test_full_url_override(self):
        """Test setting full url with env var override."""
        local_url = "mongodb://localhost"
        with patch(OS_ENVIRON_GET, Mock(return_value=local_url)), mongo_client() as client:
            self.assert_mongo_client_host_url(client, local_url)

    def test_partial_url_override(self):
        """Test setting partial url with env var overrides."""

        def _os_environ_get(variable_name, default=None):  # noqa: ANN202
            """Mock method for os.environ.get calls in shared.initialization.database."""
            values = {
                "DATABASE_USERNAME": "user",
                "DATABASE_PASSWORD": "pass",
                "DATABASE_HOST": "host",
                "DATABASE_PORT": 4242,
            }
            return values.get(variable_name, default)

        with patch(OS_ENVIRON_GET, Mock(side_effect=_os_environ_get)), mongo_client() as client:
            self.assert_mongo_client_host_url(client, "mongodb://user:pass@host:4242")
