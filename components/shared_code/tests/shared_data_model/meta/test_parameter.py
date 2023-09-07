"""Unit tests for the parameter model."""

from pydantic import HttpUrl

from shared_data_model.meta.parameter import Parameter
from shared_data_model.parameters import ParameterType

from .base import MetaModelTestCase


class ParameterTest(MetaModelTestCase):
    """Parameter unit tests."""

    MODEL = Parameter

    TOO_FEW_VALUES = "Parameter Parameter is multiple choice but has fewer than two values"

    def test_check_help_and_help_url(self):
        """Test that a parameter can only have one of help and help URL."""
        self.check_validation_error(
            "Parameter Parameter has both help and help_url",
            name="Parameter",
            type=ParameterType.STRING,
            help="Help.",
            help_url=HttpUrl("https://help.example.org"),
            metrics=["loc"],
        )
        self.check_validation_error(
            "The help of Parameter does not end with punctuation",
            name="Parameter",
            type=ParameterType.STRING,
            help="Help",
            metrics=["loc"],
        )

    def test_check_api_values_imply_values(self):
        """Test that if a parameter has API values it also has values."""
        self.check_validation_error(
            "Parameter Parameter has api_values but no values",
            name="Parameter",
            type=ParameterType.STRING,
            api_values={"value": "api_value"},
            metrics=["loc"],
        )

    def test_check_api_values_subset_of_values(self):
        """Test that the parameter API values are a subset of the parameter values."""
        expected_error = "Parameter Parameter has api_values keys that are not listed in values"
        self.check_validation_error(
            expected_error,
            name="Parameter",
            type=ParameterType.STRING,
            values=["value"],
            api_values={"other_value": "api_value"},
            metrics=["loc"],
        )

    def test_check_placeholder(self):
        """Test that multiple choice parameters need a placeholder."""
        expected_error = "Parameter Parameter is multiple choice but has no placeholder"
        self.check_validation_error(expected_error, name="Parameter", type="multiple_choice", metrics=["loc"])

    def test_check_default_value(self):
        """Test that multiple choice parameters have a list as default value."""
        self.check_validation_error(
            "Parameter Parameter is multiple choice but default_value is not a list",
            name="Parameter",
            type="multiple_choice",
            metrics=["loc"],
            placeholder="placeholder",
        )

    def test_check_default_value_empty(self):
        """Test that multiple choice parameters with addition have an empty list as default value."""
        expected_error = "Parameter Parameter is multiple choice with addition but default_value is not empty"
        self.check_validation_error(
            expected_error,
            name="Parameter",
            type="multiple_choice_with_addition",
            default_value=["value"],
            metrics=["loc"],
            placeholder="placeholder",
        )

    def test_check_values_too_few(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_validation_error(
            self.TOO_FEW_VALUES,
            name="Parameter",
            type="multiple_choice",
            values=["value"],
            metrics=["loc"],
            placeholder="placeholder",
            default_value=[],
        )

    def test_check_values_zero(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_validation_error(
            self.TOO_FEW_VALUES,
            name="Parameter",
            type="multiple_choice",
            values=[],
            metrics=["loc"],
            placeholder="placeholder",
            default_value=[],
        )

    def test_check_values_missing(self):
        """Test that multiple choice parameters have at least two values."""
        self.check_validation_error(
            self.TOO_FEW_VALUES,
            name="Parameter",
            type="multiple_choice",
            metrics=["loc"],
            placeholder="placeholder",
            default_value=[],
        )

    def test_check_values_not_empty(self):
        """Test that multiple choice parameters with addition have no values."""
        expected_error = "Parameter Parameter is multiple choice with addition but has values"
        self.check_validation_error(
            expected_error,
            name="Parameter",
            type="multiple_choice_with_addition",
            values=["value"],
            metrics=["loc"],
            placeholder="placeholder",
            default_value=[],
        )
