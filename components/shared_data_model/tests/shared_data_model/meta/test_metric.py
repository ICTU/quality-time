"""Unit tests for the metric meta model."""

from shared_data_model.meta.metric import Metric, Metrics

from .base import MetaModelTestCase


class MetricTest(MetaModelTestCase):
    """Metric unit tests."""

    MODEL = Metric

    def test_addition(self):
        """Test that an invalid addition value throws a validation error."""
        message = "value is not a valid enumeration member; permitted: 'max', 'min', 'sum'"
        self.check_validation_error(message, addition="invalid")

    def test_direction(self):
        """Test that an invalid direction value throws a validation error."""
        self.check_validation_error("value is not a valid enumeration member; permitted: '<', '>'", direction="<>")

    def test_get_item(self):
        """Test that metrics can be retrieved by key."""
        metric_kwargs = dict(name="Name", description="Description", sources=["source_type"])
        metrics = Metrics.parse_obj(dict(metric_type=metric_kwargs))
        self.assertEqual(Metric(**metric_kwargs), metrics["metric_type"])
