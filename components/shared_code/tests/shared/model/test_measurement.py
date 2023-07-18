"""Test the measurements model."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from packaging.version import Version

from shared.model.measurement import (
    Measurement,
    ScaleMeasurement,
    VersionNumberScaleMeasurement,
)
from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.type import SourceId

from tests.fixtures import METRIC_ID, SOURCE_ID, SOURCE_ID2
from tests.shared.base import DataModelTestCase


class MeasurementTestCase(DataModelTestCase):
    """Base class for measurement unit tests."""

    def metric(
        self,
        metric_type: str = "tests",
        addition: str = "sum",
        sources: dict[SourceId, Source] | None = None,
        **kwargs,
    ) -> Metric:
        """Create a metric fixture."""
        metric_data = dict(
            addition=addition,
            type=metric_type,
            sources={
                SOURCE_ID: {"type": "azure_devops"},
                SOURCE_ID2: {"type": "azure_devops"},
            }
            if sources is None
            else sources,
            **kwargs,
        )
        return Metric(self.DATA_MODEL, metric_data, METRIC_ID)

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
        """The status_start should return the start of the measurement."""
        measurement = Measurement(self.metric(), start="now")
        s_m = ScaleMeasurement(previous_scale_measurement=None, measurement=measurement)
        s_m.update_value_and_status()
        self.assertIs(s_m.status_start(), "now")

    def test_previous_status_start_empty(self):
        """The status_start should return the start of the measurement."""
        previous_s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=Measurement(self.metric(), start="yesterday"),
            status_start=None,
            status=None,
        )
        s_m = ScaleMeasurement(
            previous_scale_measurement=previous_s_m,
            measurement=Measurement(self.metric(), start="now"),
        )
        s_m.update_value_and_status()
        self.assertIsNone(s_m.status_start())

    def test_status_start_unchanged(self):
        """The status_start should be the status start of the previous measurement if the status is unchanged."""
        previous_s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=Measurement(self.metric(), start="yesterday"),
            status_start="yesterday",
            status=None,
        )
        s_m = ScaleMeasurement(
            previous_scale_measurement=previous_s_m,
            measurement=Measurement(self.metric(), start="today"),
            status=None,
        )
        s_m.update_value_and_status()
        self.assertEqual(s_m.status_start(), "yesterday")

    def test_set_status_start_changed(self):
        """Test status_start."""
        previous_s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=Measurement(self.metric(), start="yesterday"),
            status_start="yesterday",
            status="target_met",
        )
        measurement = Measurement(self.metric(), start="today")
        s_m = ScaleMeasurement(previous_scale_measurement=previous_s_m, measurement=measurement)
        s_m.update_value_and_status()
        self.assertEqual(s_m.status_start(), measurement["start"])

    @patch.object(
        ScaleMeasurement,
        "_better_or_equal",
        lambda _self, value, target: value <= target,
    )
    def test_calculate_status_debt_target(self):
        """Test calculate status."""
        measurement = Measurement(self.metric(accept_debt=True))
        s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            target=1,
            near_target=2,
            debt_target=3,
        )
        status = s_m._ScaleMeasurement__calculate_status(3)  # noqa: SLF001
        self.assertEqual(status, "debt_target_met")

    @patch.object(
        ScaleMeasurement,
        "_better_or_equal",
        lambda _self, value, target: value <= target,
    )
    def test_calculate_status_near_target(self):
        """Test calculate status."""
        measurement = Measurement(self.metric())
        s_m = ScaleMeasurement(
            previous_scale_measurement=None,
            measurement=measurement,
            target=1,
            debt_target=2,
            near_target=3,
        )
        status = s_m._ScaleMeasurement__calculate_status(3)  # noqa: SLF001
        self.assertEqual(status, "near_target_met")


class VersionNumberScaleMeasurementTest(MeasurementTestCase):
    """Tests for the version numner measurement class."""

    def test_calculate_value(self):
        """Test calculate value."""
        measurement = Measurement(self.metric())
        vn_s_m = VersionNumberScaleMeasurement(previous_scale_measurement=None, measurement=measurement)
        value = vn_s_m._calculate_value()  # noqa: SLF001
        self.assertEqual(value, "0")

    def test_better_or_equal(self):
        """Test calculate value."""
        measurement = Measurement(self.metric())
        vn_s_m = VersionNumberScaleMeasurement(previous_scale_measurement=None, measurement=measurement, direction="<")
        better_or_equal = vn_s_m._better_or_equal("0", "1")  # noqa: SLF001
        self.assertTrue(better_or_equal)

    def test_parse_version(self):
        """Parse a None version."""
        version = VersionNumberScaleMeasurement.parse_version(None)
        self.assertEqual(Version("0"), version)

    def test_parse_invalid_version(self):
        """Parse an invalid version."""
        version = VersionNumberScaleMeasurement.parse_version("This is not a version number")
        self.assertEqual(Version("0"), version)


class MeasurementTest(MeasurementTestCase):
    """Unit tests for the measurement class."""

    def test_copy(self):
        """Test that the copy has new timestamps."""
        timestamp = "2020-01-01"
        measurement_copy = Measurement(self.metric(), start=timestamp, end=timestamp).copy()
        self.assertNotIn(timestamp, measurement_copy["start"], measurement_copy["end"])

    def test_equals(self):
        """Test that equal measurements compare equal."""
        measurement_1 = Measurement(self.metric())
        measurement_2 = Measurement(self.metric())
        self.assertTrue(measurement_1.equals(measurement_2))

    def test_equals_with_different_scales(self):
        """Test that measurements with different status are not equal."""
        measurement_1 = Measurement(self.metric(), {"count": {"status": "target_met"}})
        measurement_2 = Measurement(self.metric(), {"count": {"status": "target_not_met"}})
        self.assertFalse(measurement_1.equals(measurement_2))

    def test_equals_with_different_sources(self):
        """Test that measurements with different sources are not equal."""
        measurement_1 = Measurement(self.metric(), sources=[{"source_uuid": SOURCE_ID}])
        measurement_2 = Measurement(self.metric())
        self.assertFalse(measurement_1.equals(measurement_2))

    def test_equals_with_different_issue_statuses(self):
        """Test that measurements with different issue statuses are not equal."""
        measurement_1 = Measurement(self.metric(), issue_status=[{"issue_id": "issue_id"}])
        measurement_2 = Measurement(self.metric())
        self.assertFalse(measurement_1.equals(measurement_2))

    def test_entity_user_data(self):
        """Copy the user data."""
        measurement_1 = Measurement(
            self.metric(),
            sources=[
                {
                    "source_uuid": SOURCE_ID,
                    "type": "azure_devops",
                    "entity_user_data": {"key": {}},
                },
            ],
        )
        measurement_2 = Measurement(
            self.metric(),
            sources=[
                {"source_uuid": SOURCE_ID, "type": "azure_devops"},
                {"source_uuid": SOURCE_ID2, "type": "azure_devops"},
            ],
        )

        measurement_2.copy_entity_user_data(measurement_1)
        for source in measurement_2.sources():
            if source["source_uuid"] == SOURCE_ID:
                self.assertTrue("entity_user_data" in source)

    def test_copy_first_seen_timestamps(self):
        """Test that the first seen timestamps can be copied."""
        measurement_1 = Measurement(
            self.metric(),
            sources=[
                {
                    "source_uuid": SOURCE_ID,
                    "type": "azure_devops",
                    "entities": [{"key": "key1", "first_seen": "2023-07-15"}],
                },
            ],
        )
        measurement_2 = Measurement(
            self.metric(),
            sources=[
                {
                    "source_uuid": SOURCE_ID,
                    "type": "azure_devops",
                    "entities": [{"key": "key1", "first_seen": "2023-07-16"}],
                },
                {
                    "source_uuid": SOURCE_ID2,
                    "type": "azure_devops",
                    "entities": [{"key": "key1", "first_seen": "2023-07-17"}],
                },
            ],
        )
        measurement_2.copy_entity_first_seen_timestamps(measurement_1)
        self.assertEqual("2023-07-15", measurement_2["sources"][0]["entities"][0]["first_seen"])
        self.assertEqual("2023-07-17", measurement_2["sources"][1]["entities"][0]["first_seen"])

    def test_status_missing(self):
        """Test the measurement status is missing if the measurement has no sources."""
        measurement = Measurement(self.metric())
        self.assertEqual(None, measurement.status())

    def test_status_target_met(self):
        """Test the measurement status is target met if the measurement has sources with the right measurements."""
        measurement = self.measurement(
            self.metric(),
            sources=[
                {"source_uuid": SOURCE_ID, "value": "0", "total": "100", "parse_error": None, "connection_error": None},
                {
                    "source_uuid": SOURCE_ID2,
                    "value": "0",
                    "total": "100",
                    "parse_error": None,
                    "connection_error": None,
                },
            ],
        )
        self.assertEqual("target_met", measurement.status())

    def test_status_informative(self):
        """Test the measurement status is informative if the metric has target evaluation turned off."""
        measurement = self.measurement(
            self.metric(evaluate_targets=False),
            sources=[
                {"source_uuid": SOURCE_ID, "value": "5", "total": "100", "parse_error": None, "connection_error": None},
                {
                    "source_uuid": SOURCE_ID2,
                    "value": "7",
                    "total": "100",
                    "parse_error": None,
                    "connection_error": None,
                },
            ],
        )
        self.assertEqual("informative", measurement.status())

    def test_debt_target_expired(self):
        """Test that the debt target is considered to be expired when all issues have been done."""
        measurement = self.measurement(
            self.metric(accept_debt=True, debt_target="100", issue_ids=["FOO-40"]),
            count={"debt_target": "100"},
            issue_status=[{"status_category": "done", "issue_id": "FOO-40"}],
        )
        self.assertTrue(measurement.debt_target_expired())

    def test_debt_target_not_expired(self):
        """Test that the debt target is not considered to be expired without issues."""
        measurement = self.measurement(
            self.metric(accept_debt=True, debt_target="100"),
            count={"debt_target": "100"},
            issue_status=[],
        )
        self.assertFalse(measurement.debt_target_expired())

    def test_debt_target_not_expired_when_new_issue_added(self):
        """Test that debt target is not expired when a new issue is added."""
        measurement = self.measurement(
            self.metric(accept_debt=True, debt_target="100", issue_ids=["FOO-41", "FOO-42"]),
            count={"debt_target": "100"},
            issue_status=[{"status_category": "done", "issue_id": "FOO-41"}],
        )
        self.assertFalse(measurement.debt_target_expired())

    def test_accept_missing_sources_as_tech_debt(self):
        """Test that the fact that no sources have been configured can be accepted as technical debt."""
        metric = Metric(self.DATA_MODEL, {"addition": "sum", "type": "tests", "accept_debt": True}, METRIC_ID)
        measurement = self.measurement(metric)
        self.assertEqual("debt_target_met", measurement.status())

    def test_accept_missing_sources_as_tech_debt_expired(self):
        """Test that having no sources accepted as technical debt can also expire."""
        metric = Metric(
            self.DATA_MODEL,
            {"addition": "sum", "type": "tests", "accept_debt": True, "debt_end_date": "2020-01-01"},
            METRIC_ID,
        )
        measurement = self.measurement(metric)
        self.assertIsNone(measurement.status())

    def test_sources_ok(self):
        """Test that the measurement sources are ok if they support the metric and don't have errors."""
        measurement = self.measurement(
            self.metric(),
            sources=[
                {"source_uuid": SOURCE_ID, "value": "5", "total": "100", "parse_error": None, "connection_error": None},
                {
                    "source_uuid": SOURCE_ID2,
                    "value": "7",
                    "total": "100",
                    "parse_error": None,
                    "connection_error": None,
                },
            ],
        )
        self.assertTrue(measurement.sources_ok())

    def test_sources_not_ok_on_parse_error(self):
        """Test that the measurement sources are not ok if they have errors."""
        measurement = self.measurement(
            self.metric(),
            sources=[
                {
                    "source_uuid": SOURCE_ID,
                    "value": None,
                    "total": None,
                    "parse_error": "Oops!",
                    "connection_error": None,
                },
                {
                    "source_uuid": SOURCE_ID2,
                    "value": "7",
                    "total": "100",
                    "parse_error": None,
                    "connection_error": None,
                },
            ],
        )
        self.assertFalse(measurement.sources_ok())

    def test_sources_not_ok_on_connection_error(self):
        """Test that the measurement sources are not ok if they have errors."""
        measurement = self.measurement(
            self.metric(),
            sources=[
                {
                    "source_uuid": SOURCE_ID,
                    "value": None,
                    "total": None,
                    "parse_error": None,
                    "connection_error": "Oops!",
                },
                {
                    "source_uuid": SOURCE_ID2,
                    "value": "7",
                    "total": "100",
                    "parse_error": None,
                    "connection_error": None,
                },
            ],
        )
        self.assertFalse(measurement.sources_ok())

    def test_sources_not_ok_on_config_error(self):
        """Test that the measurement sources are not ok if they have errors."""
        measurement = self.measurement(
            self.metric(metric_type="sentiment"),
            sources=[
                {"source_uuid": SOURCE_ID, "value": "5", "total": "100", "parse_error": None, "connection_error": None},
                {
                    "source_uuid": SOURCE_ID2,
                    "value": "7",
                    "total": "100",
                    "parse_error": None,
                    "connection_error": None,
                },
            ],
        )
        self.assertFalse(measurement.sources_ok())


class SummarizeMeasurementTest(MeasurementTestCase):
    """Unit tests for the measurement summary."""

    def test_summarize(self):
        """Test the measurement summary."""
        measurement = self.measurement(self.metric())
        self.assertEqual(
            {
                "count": {"value": None, "status": None},
                "start": measurement["start"],
                "end": measurement["end"],
            },
            measurement.summarize(),
        )

    def test_summarize_with_non_default_start_date(self):
        """Test the measurement summary when the measurement has a specific start date."""
        timestamp = (datetime.now(tz=UTC) - timedelta(days=1)).replace(microsecond=0).isoformat()
        measurement = self.measurement(self.metric(), start=timestamp, end=timestamp)
        self.assertEqual(
            {"count": {"value": None, "status": None}, "start": timestamp, "end": timestamp},
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
        parse_error: str | None = None,
        total: str | None = None,
        value: str | None = None,
    ) -> Source:
        """Create a source fixture."""
        self.source_count += 1
        source_number = "" if self.source_count == 1 else str(self.source_count)
        return Source(
            f"source{source_number}",
            metric,
            {
                "source_uuid": f"source{source_number}",
                "connection_error": None,
                "parse_error": parse_error,
                "total": total,
                "value": value,
            },
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
        metric = self.metric(sources={SOURCE_ID: {"type": "junit"}})
        source = self.source(metric, value="10")
        source["entities"] = [
            {"key": "entity1"},
            {"key": "entity2"},
            {"key": "entity3"},
            {"key": "entity4"},
        ]
        source["entity_user_data"] = {
            "entity1": {"status": "fixed"},
            "entity2": {"status": "wont_fix", "status_end_date": "3000-01-01T00:00:00+00:00"},
            "entity3": {"status": "false_positive", "status_end_date": "2022-02-05T00:00:00+00:00"},
        }
        measurement = self.measurement(metric, sources=[source])
        self.assertEqual("8", measurement["count"]["value"])

    def test_value_ignored_entities(self):
        """Test that the summed value of ignored entities is subtracted, if an entity attribute should be used."""
        metric = self.metric()
        source = self.source(metric, value="10")
        source["entities"] = [
            {"key": "entity1", "counted_tests": 3},
            {"key": "entity2", "counted_tests": 5},
            {"key": "entity3", "counted_tests": 2},
            {"key": "entity4", "counted_tests": 10},
        ]
        source["entity_user_data"] = {
            "entity1": {"status": "fixed"},
            "entity2": {"status": "wont_fix"},
            "entity3": {"status": "false_positive"},
        }
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
        metric = self.metric(direction="<")
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
        metric = self.metric(direction="<", addition="min")
        sources = [
            self.source(metric, value="10", total="70"),
            self.source(metric, value="20", total="50"),
        ]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("14", measurement["percentage"]["value"])

    def test_min_of_percentages_with_zero_denominator(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        metric = self.metric(direction="<", addition="min")
        sources = [
            self.source(metric, value="10", total="70"),
            self.source(metric, value="0", total="0"),
        ]
        measurement = self.measurement(metric, sources=sources)
        self.assertEqual("0", measurement["percentage"]["value"])
