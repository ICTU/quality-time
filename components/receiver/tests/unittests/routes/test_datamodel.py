"""Unit tests for the datamodel routes."""

import unittest
from unittest.mock import Mock

from src.routes import datamodel


class DatamodelTest(unittest.TestCase):
    """Unit tests for the datamodel route."""

    def test_get_datamodel(self):
        """Test that the datamodel can be retrieved."""
        database = Mock()
        database.datamodels.find_one.return_value = dict(_id=123)
        self.assertEqual(dict(_id="123"), datamodel.get_datamodel(database))
