"""Unit tests for the metric meta model."""

from shared_data_model.meta.metric import Metric

from .base import MetaModelTestCase


class MetricTest(MetaModelTestCase):
    """Metric unit tests."""

    MODEL = Metric

    def test_addition(self):
        """Test that an invalid addition value throws a validation error."""
        self.check_validation_error("Input should be 'max', 'min' or 'sum'", addition="invalid")

    def test_direction(self):
        """Test that an invalid direction value throws a validation error."""
        self.check_validation_error("Input should be '<' or '>'", direction="<>")

    def test_scales(self):
        """Test that a metric without scales throws a validation error."""
        self.check_validation_error(
            "List should have at least 1 item after validation, not 0",
            name="Metric",
            description="Description",
            sources=["source"],
            scales=[],
        )

    def test_default_scale(self):
        """Test that the default scale is set correctly."""
        metric = self.MODEL(
            default_scale="",
            description="Description.",
            name="Metric",
            scales=["percentage"],
            sources=["source"],
        )
        self.assertEqual("percentage", metric.default_scale)
