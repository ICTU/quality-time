"""Base classes for the model unit tests."""

import json
import unittest
from typing import ClassVar, cast

from shared_data_model import DATA_MODEL_JSON


class DataModelTestCase(unittest.TestCase):
    """Base class for unit tests that use the data model."""

    DATA_MODEL: ClassVar[dict] = {}

    @classmethod
    def setUpClass(cls) -> None:
        """Override to set up the data model."""
        cls.DATA_MODEL = cls.load_data_model()

    @staticmethod
    def load_data_model() -> dict:
        """Load the data model from the JSON dump."""
        data_model = cast(dict, json.loads(DATA_MODEL_JSON))
        data_model["_id"] = "id"
        data_model["timestamp"] = "now"
        return data_model
