"""Base class for the data model unit tests."""

import unittest

from pydantic import ValidationError


class MetaModelTestCase(unittest.TestCase):
    """Meta model test case."""

    def check_validation_error(self, expected_message: str, model, **model_kwargs) -> None:
        """Check that parsing the object with the model raises a validation error with the specified message."""
        with self.assertRaises(ValidationError) as context:
            model(**model_kwargs)
        self.assertIn(expected_message, str(context.exception))
