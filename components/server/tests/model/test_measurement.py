"""Test the measurements collection."""

import unittest

from database.measurements import calculate_measurement_value
from model.measurement import Source
from model.metric import Metric

from ..fixtures import SOURCE_ID, SOURCE_ID2


class CalculateMeasurementValueTest(unittest.TestCase):
    """Unit tests for calculating the measurement value from one or more source measurements."""

    def setUp(self):
        """Override to set up a metric fixture."""
        self.data_model = dict(
            metrics=dict(metric_type=dict(direction="<")),
            sources=dict(
                source_type=dict(entities=dict(metric_type=dict(attributes=[dict(key="story_points", type="integer")])))
            ),
        )
        self.metric_data = dict(
            addition="sum",
            direction="<",
            type="metric_type",
            sources={SOURCE_ID: dict(type="source_type"), SOURCE_ID2: dict(type="source_type")},
        )
        self.metric = Metric(self.data_model, self.metric_data)

    def test_no_source_measurements(self):
        """Test that the measurement value is None if there are no sources."""
        self.assertEqual(None, calculate_measurement_value(self.data_model, self.metric, [], "count"))

    def test_error(self):
        """Test that the measurement value is None if a source has an error."""
        sources = [Source(dict(source_uuid=SOURCE_ID, parse_error="error"))]
        self.assertEqual(None, calculate_measurement_value(self.data_model, self.metric, sources, "count"))

    def test_add_two_sources(self):
        """Test that the values of two sources are added."""
        sources = [
            Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="10", total=None)),
            Source(dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="20", total=None)),
        ]
        self.assertEqual("30", calculate_measurement_value(self.data_model, self.metric, sources, "count"))

    def test_max_two_sources(self):
        """Test that the max value of two sources is returned."""
        self.metric_data["addition"] = "max"
        sources = [
            Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="10", total=None)),
            Source(dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="20", total=None)),
        ]
        self.assertEqual("20", calculate_measurement_value(self.data_model, self.metric, sources, "count"))

    def test_ignored_entities(self):
        """Test that the number of ignored entities is subtracted."""
        sources = [
            Source(
                dict(
                    source_uuid=SOURCE_ID,
                    parse_error=None,
                    connection_error=None,
                    value="10",
                    total=None,
                    entity_user_data=dict(
                        entity1=dict(status="fixed"),
                        entity2=dict(status="wont_fix"),
                        entity3=dict(status="false_positive"),
                    ),
                )
            )
        ]
        self.assertEqual("7", calculate_measurement_value(self.data_model, self.metric, sources, "count"))

    def test_value_ignored_entities(self):
        """Test that the summed value of ignored entities is subtracted, if an entity attribute should be used."""
        self.data_model["sources"]["source_type"]["entities"]["metric_type"]["measured_attribute"] = "story_points"
        sources = [
            Source(
                dict(
                    source_uuid=SOURCE_ID,
                    parse_error=None,
                    connection_error=None,
                    value="10",
                    total=None,
                    entities=[
                        dict(key="entity1", story_points=3),
                        dict(key="entity2", story_points=5),
                        dict(key="entity3", story_points=2),
                        dict(key="entity4", story_points=10),
                    ],
                    entity_user_data=dict(
                        entity1=dict(status="fixed"),
                        entity2=dict(status="wont_fix"),
                        entity3=dict(status="false_positive"),
                    ),
                )
            )
        ]
        self.assertEqual("0", calculate_measurement_value(self.data_model, self.metric, sources, "count"))

    def test_percentage(self):
        """Test a non-zero percentage."""
        sources = [
            Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="10", total="70")),
            Source(dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="20", total="50")),
        ]
        self.assertEqual("25", calculate_measurement_value(self.data_model, self.metric, sources, "percentage"))

    def test_percentage_is_zero(self):
        """Test that the percentage is zero when the total is zero and the direction is 'fewer is better'."""
        sources = [Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="0", total="0"))]
        self.assertEqual("0", calculate_measurement_value(self.data_model, self.metric, sources, "percentage"))

    def test_percentage_is_100(self):
        """Test that the percentage is 100 when the total is zero and the direction is 'more is better'."""
        self.metric_data["direction"] = ">"
        sources = [Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="0", total="0"))]
        self.assertEqual("100", calculate_measurement_value(self.data_model, self.metric, sources, "percentage"))

    def test_min_of_percentages(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        self.metric_data["addition"] = "min"
        sources = [
            Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="10", total="70")),
            Source(dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="20", total="50")),
        ]
        self.assertEqual("14", calculate_measurement_value(self.data_model, self.metric, sources, "percentage"))

    def test_min_of_percentages_with_zero_denominator(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        self.metric_data["addition"] = "min"
        sources = [
            Source(dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="10", total="70")),
            Source(dict(source_uuid=SOURCE_ID2, parse_error=None, connection_error=None, value="0", total="0")),
        ]
        self.assertEqual("0", calculate_measurement_value(self.data_model, self.metric, sources, "percentage"))
