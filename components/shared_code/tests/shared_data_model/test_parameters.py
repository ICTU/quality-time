"""Unit tests for the parameter model."""

from shared_data_model.parameters import IntegerParameter

from .meta.base import MetaModelTestCase


class IntegerParameterTest(MetaModelTestCase):
    """Integer parameter unit tests."""

    def test_check_unit(self):
        """Test that a parameter with the integer type also has a unit."""
        model_kwargs = {"name": "Parameter", "type": "integer", "metrics": ["loc"]}
        expected_message = "Parameter Parameter has no unit"
        self.check_validation_error(expected_message, IntegerParameter, **model_kwargs)
