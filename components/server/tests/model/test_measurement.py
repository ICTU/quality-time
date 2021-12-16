"""Test the measurements collection."""

import unittest

from model.measurement import Measurement
from model.metric import Metric
from model.source import Source

from ..fixtures import METRIC_ID


class MeasurementTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Base class for measurement unit tests."""

    def setUp(self):
        """Override to set up the data model."""
        self.data_model = dict(
            metrics=dict(metric_type=dict(direction="<", default_scale="count", scales=["count", "percentage"])),
            sources=dict(
                source_type=dict(entities=dict(metric_type=dict(attributes=[dict(key="story_points", type="integer")])))
            ),
        )

    def metric(self, addition="sum", direction="<") -> Metric:
        """Create a metric fixture."""
        metric_data = dict(
            addition=addition,
            direction=direction,
            type="metric_type",
            sources={"uuid-1": dict(type="source_type"), "uuid-2": dict(type="source_type")},
        )
        return Metric(self.data_model, metric_data, METRIC_ID)

    @staticmethod
    def measurement(metric: Metric, sources=None) -> Measurement:
        """Create a measurement fixture."""
        measurement = Measurement(metric, dict(sources=sources or []))
        measurement.update_measurement()
        return measurement


class SummarizeMeasurementTest(MeasurementTestCase):
    """Unit tests for the measurement summary."""

    def test_summarize(self):
        """Test the measurement summary."""
        measurement = self.measurement(self.metric())
        self.assertEqual(
            dict(count=dict(value=None, status=None), start=measurement["start"], end=measurement["end"]),
            measurement.summarize("count"),
        )


class CalculateMeasurementValueTest(MeasurementTestCase):
    """Unit tests for calculating the measurement value from one or more source measurements."""

    def setUp(self):
        """Extend to reset the source counter."""
        super().setUp()
        self.source_count = 0

    def source(self, metric: Metric, parse_error: str = None, total: str = None, value: str = None) -> Source:
        """Create a source fixture."""
        self.source_count += 1
        return Source(
            metric,
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
        measurement = self.measurement(self.metric())
        self.assertEqual(None, measurement["count"]["value"])

    def test_error(self):
        """Test that the measurement value is None if a source has an error."""
        metric = self.metric()
        measurement = self.measurement(metric, sources=[self.source(metric, parse_error="error")])
        self.assertEqual(None, measurement["count"]["value"])

    def test_add_two_sources(self):
        """Test that the values of two sources are added."""
        metric = self.metric()
        measurement = self.measurement(
            metric, sources=[self.source(metric, value="10"), self.source(metric, value="20")]
        )
        self.assertEqual("30", measurement["count"]["value"])

    def test_max_two_sources(self):
        """Test that the max value of two sources is returned."""
        metric = self.metric(addition="max")
        measurement = self.measurement(
            metric, sources=[self.source(metric, value="10"), self.source(metric, value="20")]
        )
        self.assertEqual("20", measurement["count"]["value"])

    def test_ignored_entities(self):
        """Test that the number of ignored entities is subtracted."""
        metric = self.metric()
        source = self.source(metric, value="10")
        source["entities"] = [dict(key="entity1"), dict(key="entity2"), dict(key="entity3"), dict(key="entity4")]
        source["entity_user_data"] = dict(
            entity1=dict(status="fixed"),
            entity2=dict(status="wont_fix"),
            entity3=dict(status="false_positive"),
        )
        measurement = self.measurement(metric, sources=[source])
        self.assertEqual("7", measurement["count"]["value"])

    def test_value_ignored_entities(self):
        """Test that the summed value of ignored entities is subtracted, if an entity attribute should be used."""
        self.data_model["sources"]["source_type"]["entities"]["metric_type"]["measured_attribute"] = "story_points"
        metric = self.metric()
        source = self.source(metric, value="10")
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
        measurement = self.measurement(metric, sources=[source])
        self.assertEqual("0", measurement["count"]["value"])

    def test_percentage(self):
        """Test a non-zero percentage."""
        metric = self.metric()
        sources = [self.source(metric, value="10", total="70"), self.source(metric, value="20", total="50")]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("25", measurement["percentage"]["value"])

    def test_percentage_is_zero(self):
        """Test that the percentage is zero when the total is zero and the direction is 'fewer is better'."""
        metric = self.metric()
        sources = [self.source(metric, value="0", total="0")]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("0", measurement["percentage"]["value"])

    def test_percentage_is_100(self):
        """Test that the percentage is 100 when the total is zero and the direction is 'more is better'."""
        metric = self.metric(direction=">")
        sources = [self.source(metric, value="0", total="0")]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("100", measurement["percentage"]["value"])

    def test_min_of_percentages(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        metric = self.metric(addition="min")
        sources = [self.source(metric, value="10", total="70"), self.source(metric, value="20", total="50")]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("14", measurement["percentage"]["value"])

    def test_min_of_percentages_with_zero_denominator(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        metric = self.metric(addition="min")
        sources = [self.source(metric, value="10", total="70"), self.source(metric, value="0", total="0")]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("0", measurement["percentage"]["value"])
