"""Base class for the data model unit tests."""

import unittest

from pydantic import BaseModel, ValidationError  # pylint: disable=no-name-in-module


class MetaModelTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Meta model test case."""

    MODEL = BaseModel  # Should be overridden by subclasses

    def check_validation_error(self, message, **model_kwargs):
        """Check that parsing the object with the model raises a validation error with the specified message."""
        with self.assertRaises(ValidationError) as context:
            self.MODEL.parse_obj(model_kwargs)
        self.assertIn(message, str(context.exception))
