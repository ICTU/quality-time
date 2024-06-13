"""Test the database connection parameters."""

import unittest
from unittest.mock import Mock, patch

from shared.initialization.database import client


class TestConnectionParams(unittest.TestCase):
    """Test the database connection parameters."""

    def _assert_dbclient_host_url(self, dbclient, expected_url) -> None:
        """Assert that the dbclient was initialized with expected url."""
        self.assertEqual(expected_url, dbclient._MongoClient__init_kwargs["host"])  # noqa: SLF001

    def test_default(self):
        """Test the default url."""
        db = client()
        _default_user_pass = "root:root"  # nosec  # noqa: S105
        self._assert_dbclient_host_url(db, f"mongodb://{_default_user_pass}@localhost:27017")

    def test_full_url_override(self):
        """Test setting full url with env var override."""
        local_url = "mongodb://localhost"
        with patch("shared.initialization.database.os.environ.get", Mock(return_value=local_url)):
            db = client()
        self._assert_dbclient_host_url(db, local_url)

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

        with patch("shared.initialization.database.os.environ.get", Mock(side_effect=_os_environ_get)):
            db = client()
        self._assert_dbclient_host_url(db, "mongodb://user:pass@host:4242")
