"""Test the measurements model."""

from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from packaging.version import Version

from shared.model.measurement import (
    Measurement,
    ScaleMeasurement,
    VersionNumberScaleMeasurement,
)
from shared.model.metric import Metric
from shared.model.source import Source

from ...fixtures import METRIC_ID, SOURCE_ID, SOURCE_ID2


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

    def metric(self, addition="sum", direction="<", evaluate_targets=True) -> Metric:
        """Create a metric fixture."""
        metric_data = dict(
            addition=addition,
            direction=direction,
            evaluate_targets=evaluate_targets,
            type="metric_type",
            sources={
                SOURCE_ID: dict(type="source_type"),
                SOURCE_ID2: dict(type="source_type"),
            },
        )
        return Metric(self.data_model, metric_data, METRIC_ID)

    @staticmethod
    def measurement(metric: Metric, **kwargs) -> Measurement:
        """Create a measurement fixture."""
        measurement = Measurement(metric, **kwargs)
        measurement.update_measurement()
        return measurement


class ScaleMeasurementTest(MeasurementTestCase):
    """Testing the ScaleMeasurement class."""

    def test_status(self):
        """The status should return a string apparently."""
        measurement = self.measurement(self.metric())
        s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            status="target_met",
        )
        status = s_m.status()
        self.assertIs(type(status), str)
        self.assertEqual(status, "target_met")

    def test_status_start(self):
        """The status_start should get returned."""
        measurement = self.measurement(self.metric())
        s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            status_start="yesterday",
        )
        status_start = s_m.status_start()
        self.assertEqual(status_start, "yesterday")

    def test_status_start_empty(self):
        """The status_start should return None."""
        measurement = Measurement(self.metric())
        s_m = ScaleMeasurement(previous_scale_measurement=None, measurement=measurement)
        status_start = s_m.status_start()
        self.assertIs(status_start, None)

    def test_set_status_start(self):
        """Test status_start."""
        measurement = Measurement(self.metric())
        previous_s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            status_start="yesterday",
            status="target_met",
        )
        s_m = ScaleMeasurement(
            previous_scale_measurement=previous_s_m,
            measurement=measurement,
            status_start="today",
        )
        s_m._ScaleMeasurement__set_status_start("target_met")  # pylint: disable=protected-access
        self.assertEqual(s_m.status_start(), "yesterday")

    def test_set_status_start_changed(self):
        """Test status_start."""
        measurement = Measurement(self.metric())
        previous_s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            status_start="yesterday",
            status="target_met",
        )
        s_m = ScaleMeasurement(previous_scale_measurement=previous_s_m, measurement=measurement)
        s_m._ScaleMeasurement__set_status_start("target_not_met")  # pylint: disable=protected-access
        self.assertEqual(s_m.status_start(), measurement["start"])

    def test_set_status_start_no_status_start(self):
        """Test status_start."""
        measurement = Measurement(self.metric())
        previous_s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            status="target_met",
        )
        s_m = ScaleMeasurement(previous_scale_measurement=previous_s_m, measurement=measurement)
        s_m._ScaleMeasurement__set_status_start("target_met")  # pylint: disable=protected-access
        self.assertIs(s_m.status_start(), None)

    @patch.object(Metric, "accept_debt_expired", lambda self: False)
    @patch.object(
        ScaleMeasurement,
        "_better_or_equal",
        lambda self, value, target: value <= target,
    )
    def test_calculate_status_debt_target(self):
        """Test calculate status."""
        measurement = Measurement(self.metric())
        s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            target=1,
            near_target=2,
            debt_target=3,
        )
        status = s_m._ScaleMeasurement__calculate_status(2.5)  # pylint: disable=protected-access
        self.assertEqual(status, "debt_target_met")

    @patch.object(Metric, "accept_debt_expired", lambda self: True)
    @patch.object(
        ScaleMeasurement,
        "_better_or_equal",
        lambda self, value, target: value <= target,
    )
    def test_calculate_status_near_target(self):
        """Test calculate status."""
        measurement = Measurement(self.metric())
        s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            target=1,
            near_target=2,
            debt_target=3,
        )
        status = s_m._ScaleMeasurement__calculate_status(2)  # pylint: disable=protected-access
        self.assertEqual(status, "near_target_met")


class VersionNumberScaleMeasurementTest(MeasurementTestCase):
    """Tests for the version numner measurement class."""

    def test_calculate_value(self):
        """Test calculate value."""
        measurement = Measurement(self.metric())
        vn_s_m = VersionNumberScaleMeasurement(previous_scale_measurement=None, measurement=measurement)
        value = vn_s_m._calculate_value()  # pylint: disable=protected-access
        self.assertEqual(value, "0")

    def test_better_or_equal(self):
        """Test calculate value."""
        measurement = Measurement(self.metric())
        vn_s_m = VersionNumberScaleMeasurement(previous_scale_measurement=None, measurement=measurement, direction="<")
        better_or_equal = vn_s_m._better_or_equal("0", "1")  # pylint: disable=protected-access
        self.assertTrue(better_or_equal)

    def test_parse_version(self):
        """Parse a None version."""
        version = VersionNumberScaleMeasurement.parse_version(None)
        self.assertEqual(Version("0"), version)


class MeasurementTest(MeasurementTestCase):
    """Unit tests for the measurement class."""

    def test_copy(self):
        """Test that the copy has new timestamps."""
        timestamp = "2020-01-01"
        measurement_copy = Measurement(self.metric(), start=timestamp, end=timestamp).copy()
        self.assertNotIn(timestamp, measurement_copy["start"], measurement_copy["end"])

    def test_equals(self):
        """Test that metrics are equal."""
        measurement_1 = Measurement(self.metric())
        measurement_2 = Measurement(self.metric())
        self.assertTrue(measurement_1.equals(measurement_2))

    def test_entity_user_data(self):
        """Copy the user data."""
        measurement_1 = Measurement(
            self.metric(),
            sources=[
                dict(
                    source_uuid=SOURCE_ID,
                    type="source_type",
                    entity_user_data={"key": {}},
                )
            ],
        )
        measurement_2 = Measurement(
            self.metric(),
            sources=[
                dict(source_uuid=SOURCE_ID, type="source_type"),
                dict(source_uuid=SOURCE_ID2, type="source_type"),
            ],
        )

        measurement_2.copy_entity_user_data(measurement_1)
        for source in measurement_2.sources():
            if source["source_uuid"] == SOURCE_ID:
                self.assertTrue("entity_user_data" in source)

    def test_status_missing(self):
        """Test the measurement status is missing if the measurement has no sources."""
        measurement = Measurement(self.metric())
        self.assertEqual(None, measurement.status())

    def test_status_target_met(self):
        """Test the measurement status is target met if the measurement has sources with the right measurements."""
        measurement = self.measurement(
            self.metric(),
            sources=[
                dict(source_uuid=SOURCE_ID, value="0", total="100", parse_error=None, connection_error=None),
                dict(source_uuid=SOURCE_ID2, value="0", total="100", parse_error=None, connection_error=None),
            ],
        )
        self.assertEqual("target_met", measurement.status())

    def test_status_informative(self):
        """Test the measurement status is informative if the metric has target evaluation turned off."""
        measurement = self.measurement(
            self.metric(evaluate_targets=False),
            sources=[
                dict(source_uuid=SOURCE_ID, value="5", total="100", parse_error=None, connection_error=None),
                dict(source_uuid=SOURCE_ID2, value="7", total="100", parse_error=None, connection_error=None),
            ],
        )
        self.assertEqual("informative", measurement.status())


class SummarizeMeasurementTest(MeasurementTestCase):
    """Unit tests for the measurement summary."""

    def test_summarize(self):
        """Test the measurement summary."""
        measurement = self.measurement(self.metric())
        self.assertEqual(
            dict(
                count=dict(value=None, status=None),
                start=measurement["start"],
                end=measurement["end"],
            ),
            measurement.summarize(),
        )

    def test_summarize_with_non_default_start_date(self):
        """Test the measurement summary when the measurement has a specific start date."""
        timestamp = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat()
        measurement = self.measurement(self.metric(), start=timestamp, end=timestamp)
        self.assertEqual(
            dict(count=dict(value=None, status=None), start=timestamp, end=timestamp),
            measurement.summarize(),
        )


class CalculateMeasurementValueTest(MeasurementTestCase):
    """Unit tests for calculating the measurement value from one or more source measurements."""

    def setUp(self):
        """Extend to reset the source counter."""
        super().setUp()
        self.source_count = 0

    def source(
        self,
        metric: Metric,
        parse_error: str = None,
        total: str = None,
        value: str = None,
    ) -> Source:
        """Create a source fixture."""
        self.source_count += 1
        source_number = "" if self.source_count == 1 else str(self.source_count)
        return Source(
            f"source_uuid{source_number}",
            metric,
            dict(
                source_uuid=f"source_uuid{source_number}",
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
            metric,
            sources=[self.source(metric, value="10"), self.source(metric, value="20")],
        )
        self.assertEqual("30", measurement["count"]["value"])

    def test_max_two_sources(self):
        """Test that the max value of two sources is returned."""
        metric = self.metric(addition="max")
        measurement = self.measurement(
            metric,
            sources=[self.source(metric, value="10"), self.source(metric, value="20")],
        )
        self.assertEqual("20", measurement["count"]["value"])

    def test_ignored_entities(self):
        """Test that the number of ignored entities is subtracted."""
        metric = self.metric()
        source = self.source(metric, value="10")
        source["entities"] = [
            dict(key="entity1"),
            dict(key="entity2"),
            dict(key="entity3"),
            dict(key="entity4"),
        ]
        source["entity_user_data"] = dict(
            entity1=dict(status="fixed"),
            entity2=dict(status="wont_fix", status_end_date="3000-01-01"),
            entity3=dict(status="false_positive", status_end_date="2022-02-05"),
        )
        measurement = self.measurement(metric, sources=[source])
        self.assertEqual("8", measurement["count"]["value"])

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
        sources = [
            self.source(metric, value="10", total="70"),
            self.source(metric, value="20", total="50"),
        ]
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
        sources = [
            self.source(metric, value="10", total="70"),
            self.source(metric, value="20", total="50"),
        ]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("14", measurement["percentage"]["value"])

    def test_min_of_percentages_with_zero_denominator(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        metric = self.metric(addition="min")
        sources = [
            self.source(metric, value="10", total="70"),
            self.source(metric, value="0", total="0"),
        ]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("0", measurement["percentage"]["value"])
