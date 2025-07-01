"""Unit tests for the parameter model."""

from shared_data_model.parameters import IntegerParameter, MultipleChoiceWithoutDefaultsParameter

from .meta.base import MetaModelTestCase


class IntegerParameterTest(MetaModelTestCase):
    """Integer parameter unit tests."""

    def test_check_unit(self):
        """Test that a parameter with the integer type also has a unit."""
        model_kwargs = {"name": "Parameter", "type": "integer", "metrics": ["loc"]}
        expected_message = "Parameter Parameter has no unit"
        self.check_validation_error(expected_message, IntegerParameter, **model_kwargs)


class MultipleChoiceParameterTest(MetaModelTestCase):
    """Multiple choice parameter unit tests."""

    def test_check_default_value(self):
        """Test that a multiple choice parameter without default value reports an error if a default value is passed."""
        model_kwargs = {
            "name": "Parameter",
            "type": "multiple_choice_without_defaults",
            "metrics": ["loc"],
            "default_value": ["foo"],
        }
        expected_message = "Parameter Parameter has default value ['foo'], should be an empty list"
        self.check_validation_error(expected_message, MultipleChoiceWithoutDefaultsParameter, **model_kwargs)
