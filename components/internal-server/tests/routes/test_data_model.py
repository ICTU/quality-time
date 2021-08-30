"""Unit tests for the data model route."""

import unittest
from unittest.mock import AsyncMock, MagicMock

from routes.data_model import get_data_model


class DataModelTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the data model route."""

    def setUp(self) -> None:
        """Override to create the database fixture."""
        self.database = MagicMock()

    async def test_get_data_model(self):
        """Test that the data model endpoint returns the data model."""
        self.database.datamodels.find_one = AsyncMock(return_value=dict(_id="id", foo="bar"))
        self.assertEqual(dict(_id="id", foo="bar"), await get_data_model(self.database))

    async def test_missing_data_model(self):
        """Test that the data model endpoint returns an empty dict if the data model is missing."""
        self.database.datamodels.find_one = AsyncMock(return_value=None)
        self.assertEqual({}, await get_data_model(self.database))
