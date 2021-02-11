"""Unit tests for initialization of secrets."""

import unittest
from unittest.mock import Mock

from initialization.secrets import initialize_secrets


class TestSecrets(unittest.TestCase):
    """Unit tests for initialization of secrets."""

    def setUp(self):
        """Set up database mocks."""
        self.database = Mock()
        self.database.secrets.insert = Mock()

    def test_initialize_secrets(self):
        """Test initialization of field encryption secrets."""

        # A secret already exists
        self.database.secrets.find_one.return_value = True
        initialize_secrets(self.database)
        self.assertFalse(self.database.secrets.insert.called)

        # no secret exists yet, should insert
        self.database.secrets.find_one.return_value = None
        initialize_secrets(self.database)
        self.assertTrue(self.database.secrets.insert.called)
