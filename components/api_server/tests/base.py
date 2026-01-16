"""Base classes for the model unit tests."""

import functools
import json
import logging
import unittest
from unittest.mock import Mock
from typing import ClassVar, cast, TYPE_CHECKING

from shared_data_model import DATA_MODEL_JSON

if TYPE_CHECKING:
    from collections.abc import Callable


class DatabaseTestCase(unittest.TestCase):
    """Base class for unit tests that need a mock database."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()


class DataModelTestCase(DatabaseTestCase):
    """Base class for unit tests that use the data model."""

    DATA_MODEL: ClassVar[dict] = {}

    @classmethod
    def setUpClass(cls) -> None:
        """Override to set up the data model."""
        cls.DATA_MODEL = cls.load_data_model()

    def setUp(self):
        """Extend to set of the data models database collection."""
        super().setUp()
        self.database.datamodels.find_one.return_value = self.DATA_MODEL

    @staticmethod
    def load_data_model() -> dict:
        """Load the data model from the JSON dump."""
        data_model = cast(dict, json.loads(DATA_MODEL_JSON))
        data_model["_id"] = "id"
        data_model["timestamp"] = "now"
        return data_model


def disable_logging[ReturnType](func: Callable[..., ReturnType]):
    """Temporarily disable logging."""

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs) -> ReturnType:
        """Disable logging before calling func and re-enable it afterwards."""
        logging.disable(logging.CRITICAL)
        result = func(*args, **kwargs)
        logging.disable(logging.NOTSET)
        return result

    return wrapper_decorator
