"""Unit tests for the parameter model."""

from data.meta.parameter import Parameter

from .base import MetaModelTestCase


class ParameterTest(MetaModelTestCase):
    """Parameter unit tests."""

    MODEL = Parameter

    TOO_FEW_VALUES = "Parameter Parameter is multiple choice but has fewer than two values"

    def test_check_help_and_help_url(self):
        """Test that a parameter can only have one of help and help URL."""
        expected_error = "Parameter Parameter has both help and help_url"
        self.check_validation_error(expected_error, name="Parameter", help="Help.", help_url="https://help.example.org")

    def test_check_api_values_imply_values(self):
        """Test that if a parameter has API values it also has values."""
        expected_error = "Parameter Parameter has api_values but no values"
        self.check_validation_error(expected_error, name="Parameter", api_values=dict(value="api_value"))

    def test_check_api_values_subset_of_values(self):
        """Test that the parameter API values are a subset of the parameter values."""
        expected_error = "Parameter Parameter has api_values keys that are not listed in values"
        self.check_validation_error(
            expected_error, name="Parameter", values=["value"], api_values=dict(other_value="api_value")
        )

    def test_check_placeholder(self):
        """Test that multiple choice parameters need a placeholder."""
        expected_error = "Parameter Parameter is multiple choice but has no placeholder"
        self.check_validation_error(expected_error, name="Parameter", type="multiple_choice")

    def test_check_default_value(self):
        """Test that multiple choice parameters have a list as default value."""
        expected_error = "Parameter Parameter is multiple choice but default_value is not a list"
        self.check_validation_error(expected_error, name="Parameter", type="multiple_choice")

    def test_check_default_value_empty(self):
        """Test that multiple choice parameters with addition have an empty list as default value."""
        expected_error = "Parameter Parameter is multiple choice with addition but default_value is not empty"
        self.check_validation_error(
            expected_error, name="Parameter", type="multiple_choice_with_addition", default_value=["value"]
        )

    def test_check_values_too_few(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_validation_error(self.TOO_FEW_VALUES, name="Parameter", type="multiple_choice", values=["value"])

    def test_check_values_zero(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_validation_error(self.TOO_FEW_VALUES, name="Parameter", type="multiple_choice", values=[])

    def test_check_values_missing(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_validation_error(self.TOO_FEW_VALUES, name="Parameter", type="multiple_choice")

    def test_check_values_not_empty(self):
        """Test that multiple choice parameters with addition have no values."""
        expected_error = "Parameter Parameter is multiple choice with addition but has values"
        self.check_validation_error(
            expected_error, name="Parameter", type="multiple_choice_with_addition", values=["value"]
        )
