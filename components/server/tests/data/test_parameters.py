"""Unit tests for the parameter model."""

from data_model.parameters import IntegerParameter

from .meta.base import MetaModelTestCase


class IntegerParameterTest(MetaModelTestCase):
    """Integer parameter unit tests."""

    MODEL = IntegerParameter

    def test_check_unit(self):
        """Test that a parameter with the integer type also has a unit."""
        self.check_validation_error(
            "Parameter Parameter has no unit",
            name="Parameter",
            type="integer",
            metrics=[],
        )
