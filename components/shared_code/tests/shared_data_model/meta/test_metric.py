"""Unit tests for the metric meta model."""

from shared_data_model.meta.metric import Metric
from shared_data_model.meta.unit import Unit

from .base import MetaModelTestCase


class MetricTest(MetaModelTestCase):
    """Metric unit tests."""

    def check_metric_validation_error(self, expected_message: str, **model_kwargs) -> None:
        """Check the validation error when instantiation the Metric model."""
        self.check_validation_error(expected_message, Metric, **model_kwargs)

    def test_addition(self):
        """Test that an invalid addition value throws a validation error."""
        self.check_metric_validation_error("Input should be 'max', 'min' or 'sum'", addition="invalid")

    def test_direction(self):
        """Test that an invalid direction value throws a validation error."""
        self.check_metric_validation_error("Input should be '<' or '>'", direction="<>")

    def test_scales(self):
        """Test that a metric without scales throws a validation error."""
        model_kwargs = {"name": "Metric", "description": "Description", "sources": ["source"], "scales": []}
        self.check_metric_validation_error("List should have at least 1 item after validation, not 0", **model_kwargs)

    def test_default_scale(self):
        """Test that the default scale is set correctly."""
        metric = Metric(
            default_scale="",
            description="Description.",
            name="Metric",
            scales=["percentage"],
            sources=["source"],
        )
        self.assertEqual("percentage", metric.default_scale)

    def test_check_unit_with_missing_plural_form(self):
        """Test that if the unit is not none, both a singular and plural version are provided."""
        expected_message = "The plural version of the unit of Metric is missing"
        self.check_metric_validation_error(
            expected_message,
            name="Metric",
            description="Description.",
            unit_singular=Unit.VIOLATION,
            sources=["source"],
        )

    def test_check_unit_with_missing_singular_form(self):
        """Test that if the unit is not none, both a singular and plural version are provided."""
        expected_message = "The singular version of the unit of Metric is missing"
        self.check_metric_validation_error(
            expected_message,
            name="Metric",
            description="Description.",
            unit=Unit.VIOLATIONS,
            sources=["source"],
        )
