"""Base classes for the model unit tests."""

import functools
import json
import logging
import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL_JSON


class DatabaseTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Base class for unit tests that need a mock database."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()


class DataModelTestCase(DatabaseTestCase):  # skipcq: PTC-W0046
    """Base class for unit tests that use the data model."""

    @classmethod
    def setUpClass(cls) -> None:
        """Override to set up the data model."""
        cls.DATA_MODEL = cls.load_data_model()

    def setUp(self):
        """Extend to set of the data models database collection."""
        super().setUp()
        self.database.datamodels.find_one.return_value = self.DATA_MODEL

    @staticmethod
    def load_data_model():
        """Load the data model from the JSON dump."""
        data_model = json.loads(DATA_MODEL_JSON)
        data_model["_id"] = "id"
        data_model["timestamp"] = "now"
        return data_model


def disable_logging(func):
    """Decorator to temporarily disable logging."""

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        """Disable logging before calling func and reenable it afterwards."""
        logging.disable(logging.CRITICAL)  # skipcq: PY-A6006
        result = func(*args, **kwargs)
        logging.disable(logging.NOTSET)  # skipcq: PY-A6006
        return result

    return wrapper_decorator
