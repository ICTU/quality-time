"""Base class for unit tests."""

import json
import unittest
from typing import ClassVar

from shared_data_model import DATA_MODEL_JSON


class DataModelTestCase(unittest.TestCase):
    """Base class for unit tests that use the data model from the database."""

    DATA_MODEL: ClassVar[dict] = {}

    @classmethod
    def setUpClass(cls) -> None:
        """Override to set up the data model."""
        cls.DATA_MODEL = json.loads(DATA_MODEL_JSON)
        cls.DATA_MODEL["_id"] = "id"
        cls.DATA_MODEL["timestamp"] = "now"
