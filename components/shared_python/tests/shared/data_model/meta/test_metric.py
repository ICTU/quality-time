"""Unit tests for the metric meta model."""

from shared.data_model.meta.metric import Metric

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

    def test_default_source(self):
        """Test that the default source is set when the metric has one source."""
        metric = Metric.parse_obj(dict(name="Name", description="Description.", sources=["source"]))
        self.assertEqual("source", metric.default_source)

    def test_default_source_none(self):
        """Test that the default source can't be None."""
        metric = Metric.parse_obj(
            dict(name="Name", description="Description.", default_source=None, sources=["source"])
        )
        self.assertEqual("source", metric.default_source)

    def test_default_source_not_listed_as_source(self):
        """Test that the default source must be listed as source."""
        message = "Default source 'missing' is not listed as source"
        self.check_validation_error(message, default_source="missing", sources=["source"])

    def test_default_source_mandatory_on_many_sources(self):
        """Test that a default source is mandatory when there is more than one source != the manual number source."""
        self.check_validation_error("Default source 'None' is not listed as source", sources=["source1", "source2"])
