"""Unit tests for the env module."""

import os
import unittest
from unittest.mock import patch

from shared.utils.env import getenv, loadenv


class GetEnvTest(unittest.TestCase):
    """Unit tests for the getenv function."""

    def test_missing_key(self):
        """Test a missing environment variable."""
        self.assertEqual("", getenv("key"))

    @patch.dict(os.environ, {"key": "value"})
    def test_existing_key(self):
        """Test an existing environment variable."""
        self.assertEqual("value", getenv("key"))


@patch("shared.utils.env.load_dotenv")
class LoadEnvTest(unittest.TestCase):
    """Unit tests for the loadenv function."""

    def test_load_one_file(self, load_dotenv):
        """Test that a .env file is loaded."""
        load_dotenv.return_value = None
        loadenv(".env")
        load_dotenv.assert_called_once()

    def test_load_two_files(self, load_dotenv):
        """Test that two .env files are loaded."""
        load_dotenv.return_value = None
        loadenv(".env", "default.env")
        self.assertEqual(load_dotenv.call_count, 2)
