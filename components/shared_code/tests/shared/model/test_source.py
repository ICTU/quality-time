"""Test the source model."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzutc

from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.functions import iso_timestamp

from tests.fixtures import METRIC_ID, SOURCE_ID, SOURCE_LOCATION_ID, create_source_location


class SourceTest(unittest.TestCase):
    """Test the source model."""

    def test_copy_entity_user_data(self):
        """Test copy entity user data."""
        now = iso_timestamp()
        long_ago = (datetime.now(tz=tzutc()) - timedelta(days=30)).isoformat()
        old_eud = {
            "key_1": {"orphaned_since": now},
            "key_2": {"orphaned_since": long_ago},
            "key_3": {"orphaned_since": now},
            "key_4": {},
        }

        old_source = Source(SOURCE_ID, metric=None, entity_user_data=old_eud)

        new_entities = [{"key": "key_3"}, {"key": "key_4"}]

        new_source = Source(SOURCE_ID, metric=None, entities=new_entities)

        new_source.copy_entity_user_data(old_source)

        self.assertIn("entity_user_data", new_source)
        self.assertIn("key_1", new_source["entity_user_data"])
        self.assertNotIn("key_2", new_source["entity_user_data"])
        self.assertIn("key_3", new_source["entity_user_data"])
        self.assertIn("key_4", new_source["entity_user_data"])
        self.assertNotIn("orphaned_since", new_source["entity_user_data"]["key_3"])

    def test_name(self):
        """Test that we get the expected name."""
        source = Source(SOURCE_ID, metric=None, name="test")
        self.assertEqual(source.name, "test")

    def test_type(self):
        """Test that we get the expected type."""
        source = Source(SOURCE_ID, metric=None, type="test")
        self.assertEqual(source.type, "test")

    def test_location(self):
        """Test that the source location can be retrieved via the metric."""
        metric = Metric({}, {"type": "violations", "sources": {}}, METRIC_ID)
        metric.source_locations = {SOURCE_LOCATION_ID: create_source_location()}
        source = Source(SOURCE_ID, metric=metric, source_location=SOURCE_LOCATION_ID)
        self.assertEqual(create_source_location(), source.location)

    def test_location_without_source_location(self):
        """Test that the source location is empty when the source does not reference a source location."""
        metric = Metric({}, {"type": "violations", "sources": {}}, METRIC_ID)
        metric.source_locations = {SOURCE_LOCATION_ID: create_source_location()}
        self.assertEqual({}, Source(SOURCE_ID, metric=metric).location)
        self.assertEqual({}, Source(SOURCE_ID, metric=metric, source_location="").location)
        self.assertEqual({}, Source(SOURCE_ID, metric=metric, source_location="missing").location)

    def test_parameters_including_location(self):
        """Test that the location parameters are merged into the source parameters."""
        metric = Metric({}, {"type": "violations", "sources": {}}, METRIC_ID)
        metric.source_locations = {SOURCE_LOCATION_ID: create_source_location()}
        source = Source(
            SOURCE_ID,
            metric=metric,
            source_location=SOURCE_LOCATION_ID,
            parameters={"tags": ["security"]},
        )
        self.assertEqual(
            {"tags": ["security"], "url": "https://url", "password": "password"},  # nosec
            source.parameters_including_location(),
        )

    def test_parameters_including_location_does_not_overwrite_with_empty_values(self):
        """Test that empty location parameter values do not overwrite source parameters."""
        metric = Metric({}, {"type": "violations", "sources": {}}, METRIC_ID)
        metric.source_locations = {SOURCE_LOCATION_ID: create_source_location(url="", password="")}  # nosec
        source = Source(
            SOURCE_ID,
            metric=metric,
            source_location=SOURCE_LOCATION_ID,
            parameters={"url": "https://source-url"},
        )
        self.assertEqual({"url": "https://source-url"}, source.parameters_including_location())

    def test_parameters_including_location_without_location(self):
        """Test that the source parameters are returned unchanged when the source has no source location."""
        metric = Metric({}, {"type": "violations", "sources": {}}, METRIC_ID)
        source = Source(SOURCE_ID, metric=metric, parameters={"url": "https://source-url"})
        self.assertEqual({"url": "https://source-url"}, source.parameters_including_location())

    def test_parameters_including_location_without_parameters(self):
        """Test that the location parameters are returned when the source has no parameters."""
        metric = Metric({}, {"type": "violations", "sources": {}}, METRIC_ID)
        metric.source_locations = {SOURCE_LOCATION_ID: create_source_location()}
        source = Source(SOURCE_ID, metric=metric, source_location=SOURCE_LOCATION_ID)
        self.assertEqual({"url": "https://url", "password": "password"}, source.parameters_including_location())  # nosec

    def test_copy_first_seen_timestamps(self):
        """Test that the first seen timestamps can be copied."""
        entities1 = [{"key": "key_1"}, {"key": "key_2", "first_seen": "2023-07-17"}]
        source1 = Source(SOURCE_ID, metric=None, entities=entities1)
        entities2 = [{"key": "key_1", "first_seen": "2023-07-18"}, {"key": "key_2", "first_seen": "2023-07-19"}]
        source2 = Source(SOURCE_ID, metric=None, entities=entities2)
        source2.copy_entity_first_seen_timestamps(source1)
        self.assertEqual("2023-07-18", source2["entities"][0]["first_seen"])
        self.assertEqual("2023-07-17", source2["entities"][1]["first_seen"])
