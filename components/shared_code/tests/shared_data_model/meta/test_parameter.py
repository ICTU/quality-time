"""Unit tests for the parameter model."""

from pydantic import HttpUrl

from shared_data_model.meta.parameter import Parameter
from shared_data_model.parameters import ParameterType

from .base import MetaModelTestCase


class ParameterTest(MetaModelTestCase):
    """Parameter unit tests."""

    TOO_FEW_VALUES = "Parameter Parameter is multiple choice but has fewer than two values"

    def check_parameter_validation_error(self, expected_message: str, **extra_model_kwargs) -> None:
        """Check the validation error when instantiation the Parameter model."""
        model_kwargs = {"name": "Parameter", "type": ParameterType.STRING, "metrics": ["loc"]}
        self.check_validation_error(expected_message, Parameter, **(model_kwargs | extra_model_kwargs))

    def test_check_help_and_help_url(self):
        """Test that a parameter can only have one of help and help URL."""
        help_url = HttpUrl("https://help.example.org")
        expected_message = "Parameter Parameter has both help and help_url"
        self.check_parameter_validation_error(expected_message, help="Help.", help_url=help_url)

    def test_check_help_punctuation(self):
        """Test that parameter help ends with punctuation."""
        expected_message = "The help of Parameter does not end with punctuation"
        self.check_parameter_validation_error(expected_message, help="Help")

    def test_check_api_values_imply_values(self):
        """Test that if a parameter has API values it also has values."""
        expected_message = "Parameter Parameter has api_values but no values"
        self.check_parameter_validation_error(expected_message, api_values={"value": "api_value"})

    def test_check_api_values_subset_of_values(self):
        """Test that the parameter API values are a subset of the parameter values."""
        extra_model_kwargs = {"values": ["value"], "api_values": {"other_value": "api_value"}}
        expected_message = "Parameter Parameter has api_values keys that are not listed in values"
        self.check_parameter_validation_error(expected_message, **extra_model_kwargs)

    def test_check_placeholder(self):
        """Test that multiple choice parameters need a placeholder."""
        expected_message = "Parameter Parameter is multiple choice but has no placeholder"
        self.check_parameter_validation_error(expected_message, type="multiple_choice_with_defaults")

    def test_check_default_value(self):
        """Test that multiple choice parameters have a list as default value."""
        expected_message = "Parameter Parameter is multiple choice but default_value is not a list"
        self.check_parameter_validation_error(
            expected_message, type="multiple_choice_with_defaults", placeholder="placeholder"
        )

    def test_check_default_value_empty(self):
        """Test that multiple choice parameters with addition have an empty list as default value."""
        self.check_parameter_validation_error(
            "Parameter Parameter is multiple choice with addition but default_value is not empty",
            type="multiple_choice_with_addition",
            default_value=["value"],
            placeholder="placeholder",
        )

    def test_check_values_too_few(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_parameter_validation_error(
            self.TOO_FEW_VALUES,
            type="multiple_choice_with_defaults",
            values=["value"],
            default_value=[],
            placeholder="placeholder",
        )

    def test_check_values_zero(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_parameter_validation_error(
            self.TOO_FEW_VALUES,
            type="multiple_choice_with_defaults",
            values=[],
            default_value=[],
            placeholder="placeholder",
        )

    def test_check_values_missing(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_parameter_validation_error(
            self.TOO_FEW_VALUES,
            type="multiple_choice_with_defaults",
            default_value=[],
            placeholder="placeholder",
        )

    def test_check_values_not_empty(self):
        """Test that multiple choice parameters with addition have no values."""
        self.check_parameter_validation_error(
            "Parameter Parameter is multiple choice with addition but has values",
            type="multiple_choice_with_addition",
            values=["value"],
            default_value=[],
            placeholder="placeholder",
        )
