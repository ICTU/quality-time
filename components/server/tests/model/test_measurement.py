"""Test the measurements collection."""

import unittest

from model.measurement import Measurement
from model.metric import Metric
from model.source import Source


class CalculateMeasurementValueTest(unittest.TestCase):
    """Unit tests for calculating the measurement value from one or more source measurements."""

    def setUp(self):
        """Override to set up a metric fixture."""
        self.data_model = dict(
            metrics=dict(metric_type=dict(direction="<", scales=["count", "percentage"])),
            sources=dict(
                source_type=dict(entities=dict(metric_type=dict(attributes=[dict(key="story_points", type="integer")])))
            ),
        )
        self.metric_data = dict(
            addition="sum",
            direction="<",
            type="metric_type",
            sources={"uuid-1": dict(type="source_type"), "uuid-2": dict(type="source_type")},
        )
        self.metric = Metric(self.data_model, self.metric_data)
        self.source_count = 0

    def source(self, parse_error: str = None, total: str = None, value: str = None) -> Source:
        """Create a source fixture."""
        self.source_count += 1
        return Source(
            self.metric,
            dict(
                source_uuid=f"uuid-{self.source_count}",
                connection_error=None,
                parse_error=parse_error,
                total=total,
                value=value,
            ),
        )

    def test_no_source_measurements(self):
        """Test that the measurement value is None if there are no sources."""
        measurement = Measurement(self.metric, dict(sources=[]))
        measurement.update_scales()
        self.assertEqual(None, measurement["count"]["value"])

    def test_error(self):
        """Test that the measurement value is None if a source has an error."""
        measurement = Measurement(self.metric, dict(sources=[self.source(parse_error="error")]))
        measurement.update_scales()
        self.assertEqual(None, measurement["count"]["value"])

    def test_add_two_sources(self):
        """Test that the values of two sources are added."""
        measurement = Measurement(self.metric, dict(sources=[self.source(value="10"), self.source(value="20")]))
        measurement.update_scales()
        self.assertEqual("30", measurement["count"]["value"])

    def test_max_two_sources(self):
        """Test that the max value of two sources is returned."""
        self.metric_data["addition"] = "max"
        measurement = Measurement(self.metric, dict(sources=[self.source(value="10"), self.source(value="20")]))
        measurement.update_scales()
        self.assertEqual("20", measurement["count"]["value"])

    def test_ignored_entities(self):
        """Test that the number of ignored entities is subtracted."""
        source = self.source(value="10")
        source["entities"] = [dict(key="entity1"), dict(key="entity2"), dict(key="entity3"), dict(key="entity4")]
        source["entity_user_data"] = dict(
            entity1=dict(status="fixed"),
            entity2=dict(status="wont_fix"),
            entity3=dict(status="false_positive"),
        )
        measurement = Measurement(self.metric, dict(sources=[source]))
        measurement.update_scales()
        self.assertEqual("7", measurement["count"]["value"])

    def test_value_ignored_entities(self):
        """Test that the summed value of ignored entities is subtracted, if an entity attribute should be used."""
        self.data_model["sources"]["source_type"]["entities"]["metric_type"]["measured_attribute"] = "story_points"
        source = self.source(value="10")
        source["entities"] = [
            dict(key="entity1", story_points=3),
            dict(key="entity2", story_points=5),
            dict(key="entity3", story_points=2),
            dict(key="entity4", story_points=10),
        ]
        source["entity_user_data"] = dict(
            entity1=dict(status="fixed"),
            entity2=dict(status="wont_fix"),
            entity3=dict(status="false_positive"),
        )
        measurement = Measurement(self.metric, dict(sources=[source]))
        measurement.update_scales()
        self.assertEqual("0", measurement["count"]["value"])

    def test_percentage(self):
        """Test a non-zero percentage."""
        sources = [self.source(value="10", total="70"), self.source(value="20", total="50")]
        measurement = Measurement(self.metric, dict(sources=sources))
        measurement.update_scales()
        self.assertEqual("25", measurement["percentage"]["value"])

    def test_percentage_is_zero(self):
        """Test that the percentage is zero when the total is zero and the direction is 'fewer is better'."""
        sources = [self.source(value="0", total="0")]
        measurement = Measurement(self.metric, dict(sources=sources))
        measurement.update_scales()
        self.assertEqual("0", measurement["percentage"]["value"])

    def test_percentage_is_100(self):
        """Test that the percentage is 100 when the total is zero and the direction is 'more is better'."""
        self.metric_data["direction"] = ">"
        sources = [self.source(value="0", total="0")]
        measurement = Measurement(self.metric, dict(sources=sources))
        measurement.update_scales()
        self.assertEqual("100", measurement["percentage"]["value"])

    def test_min_of_percentages(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        self.metric_data["addition"] = "min"
        sources = [self.source(value="10", total="70"), self.source(value="20", total="50")]
        measurement = Measurement(self.metric, dict(sources=sources))
        measurement.update_scales()
        self.assertEqual("14", measurement["percentage"]["value"])

    def test_min_of_percentages_with_zero_denominator(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        self.metric_data["addition"] = "min"
        sources = [self.source(value="10", total="70"), self.source(value="0", total="0")]
        measurement = Measurement(self.metric, dict(sources=sources))
        measurement.update_scales()
        self.assertEqual("0", measurement["percentage"]["value"])
