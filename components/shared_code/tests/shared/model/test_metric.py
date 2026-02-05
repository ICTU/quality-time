"""Test the metric model."""

import unittest
from datetime import date
from typing import TYPE_CHECKING, ClassVar

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp

from tests.fixtures import METRIC_ID, SOURCE_ID, SOURCE_ID2
from tests.shared.base import DataModelTestCase

if TYPE_CHECKING:
    from shared.utils.type import Direction, SourceId


class MetricTest(unittest.TestCase):
    """Test the metric model."""

    DATA_MODEL: ClassVar[dict] = {
        "metrics": {
            "fixture_metric_type": {"name": "fixture_metric_type", "unit": "issues"},
            "fixture_metric_type_without_name": {"unit": "issues"},
        },
    }

    def create_metric(self, **kwargs) -> Metric:
        """Return a metric fixture."""
        return Metric(self.DATA_MODEL, {"type": "fixture_metric_type", **kwargs}, METRIC_ID)

    def create_source_arguments_for_metric(
        self, multiple: bool = False, reverse: bool = False
    ) -> dict[SourceId, dict[str, dict[str, str]]]:
        """Return source arguments for creating a metric."""
        source1 = {SOURCE_ID: {"parameters": {"parameter": "value1"}}}
        if not multiple:
            return source1
        source2 = {SOURCE_ID2: {"parameters": {"parameter": "value2"}}}
        return source2 | source1 if reverse else source1 | source2

    def create_expected_summary(
        self, status: str = "", measurement_timestamp: str = "", outdated: bool = False, **kwargs
    ) -> dict[str, None | str | list | dict]:
        """Return an expected summary."""
        latest_measurement: None | dict[str, dict | list | str | bool]
        if measurement_timestamp:
            latest_measurement = {
                "count": {"value": 1, "start": measurement_timestamp},
                "end": measurement_timestamp,
                "sources": [],
                "start": measurement_timestamp,
                "status": status,
            }
            if outdated:
                latest_measurement["outdated"] = True
            recent_measurements = [
                {
                    "count": {"status": status, "value": 1},
                    "end": measurement_timestamp,
                    "start": measurement_timestamp,
                },
            ]
        else:
            latest_measurement = None
            recent_measurements = []
        summary = {
            "type": "fixture_metric_type",
            "scale": "count",
            "status": status or None,
            "status_start": None,
            "latest_measurement": latest_measurement,
            "recent_measurements": recent_measurements,
            "sources": {},
            **kwargs,
        }
        if measurement_timestamp:
            summary["issue_status"] = []
        return summary

    def test_summarize_empty_metric(self):
        """Test that a minimal metric returns a summary."""
        summary = self.create_metric().summarize([])
        self.assertDictEqual(summary, self.create_expected_summary())

    def test_summarize_metric_with_a_measurement(self):
        """Test that the metric summary includes the measurement."""
        metric = self.create_metric()
        measurement_timestamp = iso_timestamp()
        measurement = Measurement(
            metric,
            count={"value": 1, "start": measurement_timestamp},
            status="target_met",
        )
        summary = metric.summarize([measurement])
        self.assertDictEqual(summary, self.create_expected_summary("target_met", measurement_timestamp))

    def test_summarize_metric_with_an_outdated_measurement(self):
        """Test that the metric is marked outdated when the source parameters have changed."""
        metric = self.create_metric()
        measurement_timestamp = iso_timestamp()
        measurement = Measurement(
            metric,
            count={"value": 1, "start": measurement_timestamp},
            status="target_met",
            source_parameter_hash="old hash",
        )
        summary = metric.summarize([measurement])
        self.assertDictEqual(summary, self.create_expected_summary("target_met", measurement_timestamp, outdated=True))

    def test_summarize_metric_with_an_up_to_date_measurement(self):
        """Test that the metric is not marked outdated when the source parameters have not changed."""
        metric = self.create_metric()
        measurement_timestamp = iso_timestamp()
        measurement = Measurement(
            metric,
            count={"value": 1, "start": measurement_timestamp},
            status="target_met",
            source_parameter_hash=metric.source_parameter_hash(),
        )
        summary = metric.summarize([measurement])
        self.assertDictEqual(summary, self.create_expected_summary("target_met", measurement_timestamp))

    def test_summarize_metric_data(self):
        """Test that metric data is summarized."""
        summary = self.create_metric(some_metric_property="some_value").summarize([])
        self.assertDictEqual(summary, self.create_expected_summary(some_metric_property="some_value"))

    def test_debt_end_date(self):
        """Test debt end date."""
        metric = self.create_metric()
        self.assertEqual(metric.debt_end_date(), date.max.isoformat())
        metric["debt_end_date"] = ""
        self.assertEqual(metric.debt_end_date(), date.max.isoformat())
        metric["debt_end_date"] = "some date"
        self.assertEqual(metric.debt_end_date(), "some date")

    def test_name(self):
        """Test that we get the metric name from the metric."""
        self.assertEqual("name", self.create_metric(name="name").name)

    def test_missing_name(self):
        """Test that we get the metric name from the data model if the metric has no name."""
        self.assertEqual("fixture_metric_type", self.create_metric().name)

    def test_missing_default_name(self):
        """Test that the metric name is None if neither metric nor data model have a name for the metric."""
        self.assertIsNone(self.create_metric(type="fixture_metric_type_without_name").name)

    def test_unit(self):
        """Test that we get the metric unit from the metric."""
        self.assertEqual("oopsies", self.create_metric(unit="oopsies").unit)

    def test_missing_unit(self):
        """Test that we get the metric unit from the data model if the metric has no unit."""
        self.assertEqual("issues", self.create_metric().unit)

    def test_equal(self):
        """Test that a metric is equal to itself."""
        self.assertEqual(self.create_metric(), self.create_metric())

    def test_not_equal(self):
        """Test that a metric is not equal to a metric with another type."""
        self.assertEqual(self.create_metric(type="size"), self.create_metric(type="violations"))

    def test_not_equal_to_string(self):
        """Test that a metric is not equal to a string."""
        self.assertNotEqual(self.create_metric(), "foo")

    def test_source_parameter_hash_no_sources(self):
        """Test the source parameter hash for metric without sources."""
        self.assertEqual("d751713988987e9331980363e24189ce", self.create_metric().source_parameter_hash())

    def test_source_parameter_hash_one_source(self):
        """Test the source parameter hash for a metric with one source."""
        metric = self.create_metric(sources=self.create_source_arguments_for_metric())
        self.assertEqual("ee0219ddbd8adc3fb91e701addf00f0c", metric.source_parameter_hash())

    def test_source_parameter_hash_multiple_sources(self):
        """Test the source parameter hash for a metric with multiple sources."""
        metric = self.create_metric(sources=self.create_source_arguments_for_metric(multiple=True))
        self.assertEqual("8c13b82d9424e34db1a87f249d1a7e9d", metric.source_parameter_hash())

    def test_source_parameter_hash_does_not_depend_on_source_order(self):
        """Test that the source parameter hash does not depend on the order of the sources."""
        metric1 = self.create_metric(sources=self.create_source_arguments_for_metric(multiple=True))
        metric2 = self.create_metric(sources=self.create_source_arguments_for_metric(multiple=True, reverse=True))
        self.assertEqual(metric1.source_parameter_hash(), metric2.source_parameter_hash())

    def test_delete_non_existing_tag(self):
        """Test deleting a non-existing tag from a metric."""
        metric = self.create_metric()
        self.assertFalse(metric.delete_tag("foo"))
        self.assertNotIn("tags", metric)

    def test_delete_existing_tag(self):
        """Test deleting an existing tag from a metric."""
        metric = self.create_metric(tags=["foo"])
        self.assertTrue(metric.delete_tag("foo"))
        self.assertEqual([], metric["tags"])

    def test_delete_existing_tag_from_multiple_tags(self):
        """Test deleting an existing tag from a metric with multiple tags."""
        metric = self.create_metric(tags=["foo", "bar"])
        self.assertTrue(metric.delete_tag("foo"))
        self.assertEqual(["bar"], metric["tags"])

    def test_rename_non_existing_tag(self):
        """Test renaming a non-existing tag."""
        metric = self.create_metric()
        self.assertFalse(metric.rename_tag("foo", "bar"))
        self.assertNotIn("tags", metric)

    def test_rename_existing_tag(self):
        """Test renaming an existing tag."""
        metric = self.create_metric(tags=["foo"])
        self.assertTrue(metric.rename_tag("foo", "bar"))
        self.assertEqual(["bar"], metric["tags"])

    def test_rename_existing_tag_among_multiple_tags(self):
        """Test renaming an existing tag among multiple tags."""
        metric = self.create_metric(tags=["foo", "bar"])
        self.assertTrue(metric.rename_tag("bar", "baz"))
        self.assertEqual(["foo", "baz"], metric["tags"])

    def test_rename_existing_tag_to_existing_tag(self):
        """Test renaming an existing tag to an existing tag."""
        metric = self.create_metric(tags=["foo", "bar"])
        self.assertTrue(metric.rename_tag("foo", "bar"))
        self.assertEqual(["bar"], metric["tags"])


class MetricAdditionTest(DataModelTestCase):
    """Test the addition of metrics."""

    def create_metric(self, metric_type: str, **kwargs: dict[str, Direction]) -> Metric:
        """Return a metric fixture."""
        return Metric(self.DATA_MODEL, {"type": metric_type, **kwargs}, METRIC_ID)

    def test_sum(self):
        """Test that the default addition of the tests metric is to sum the results of multiple sources."""
        metric = self.create_metric("tests")
        self.assertEqual(sum, metric.addition())

    def test_sum_reversed(self):
        """Test that the addition of the tests metric is still to sum the results of multiple sources if reversed."""
        metric = self.create_metric("tests", direction="<")
        self.assertEqual(sum, metric.addition())

    def test_sum_reversed_back(self):
        """Test that the addition of the tests metric is still to sum the results if reversed back."""
        metric = self.create_metric("tests", direction=">")
        self.assertEqual(sum, metric.addition())

    def test_min(self):
        """Test that the default addition of the scalability metric is to take the minimum of multiple sources."""
        metric = self.create_metric("scalability")
        self.assertEqual(min, metric.addition())

    def test_min_reversed(self):
        """Test that the addition of the scalability metric is to take the maximum if the metric is reversed."""
        metric = self.create_metric("scalability", direction="<")
        self.assertEqual(max, metric.addition())

    def test_min_reversed_back(self):
        """Test that the addition of the scalability metric is to take the minimum if reversed back."""
        metric = self.create_metric("scalability", direction=">")
        self.assertEqual(min, metric.addition())

    def test_max(self):
        """Test that the default addition of the pipeline duration metric is to take the maximum of multiple sources."""
        metric = self.create_metric("pipeline_duration")
        self.assertEqual(max, metric.addition())

    def test_max_reversed(self):
        """Test that the addition of the pipeline duration metric is to take the minimum if the metric is reversed."""
        metric = self.create_metric("pipeline_duration", direction=">")
        self.assertEqual(min, metric.addition())

    def test_max_reversed_back(self):
        """Test that the addition of the pipeline duration metric is to take the maximum if reversed back."""
        metric = self.create_metric("pipeline_duration", direction="<")
        self.assertEqual(max, metric.addition())
