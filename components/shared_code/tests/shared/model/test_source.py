"""Test the source model."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzutc

from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.functions import iso_timestamp

from shared_test_code.base import DataModelTestCase
from shared_test_code.fixtures import METRIC_ID, SOURCE_ID


class SourceTest(unittest.TestCase):
    """Test the source model."""

    def setUp(self):
        """Set up metric fixture."""
        super().setUp()
        self.metric = Metric({}, {}, METRIC_ID)

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

        old_source = Source(SOURCE_ID, metric=self.metric, entity_user_data=old_eud)

        new_entities = [{"key": "key_3"}, {"key": "key_4"}]

        new_source = Source(SOURCE_ID, metric=self.metric, entities=new_entities)

        new_source.copy_entity_user_data(old_source)

        self.assertIn("entity_user_data", new_source)
        self.assertIn("key_1", new_source["entity_user_data"])
        self.assertNotIn("key_2", new_source["entity_user_data"])
        self.assertIn("key_3", new_source["entity_user_data"])
        self.assertIn("key_4", new_source["entity_user_data"])
        self.assertNotIn("orphaned_since", new_source["entity_user_data"]["key_3"])

    def test_copy_entity_user_data_translates_legacy_attributes(self):
        """Test that the status attributes are translated when the user data is copied to a new measurement."""
        old_eud = {"key_1": {"status": "wont_fix", "status_end_date": "3000-01-01"}}
        old_source = Source(SOURCE_ID, metric=self.metric, entity_user_data=old_eud)
        new_source = Source(SOURCE_ID, metric=self.metric, entities=[{"key": "key_1"}])
        new_source.copy_entity_user_data(old_source)
        self.assertEqual(
            {
                "excluded": True,
                "exclusion_end_date": "3000-01-01",
                "status": "wont_fix",
                "status_end_date": "3000-01-01",
            },
            new_source["entity_user_data"]["key_1"],
        )

    def test_name(self):
        """Test that we get the expected name."""
        source = Source(SOURCE_ID, metric=self.metric, name="test")
        self.assertEqual("test", source.name)

    def test_type(self):
        """Test that we get the expected type."""
        source = Source(SOURCE_ID, metric=self.metric, type="test")
        self.assertEqual("test", source.type)

    def test_copy_first_seen_timestamps(self):
        """Test that the first seen timestamps can be copied."""
        entities1 = [{"key": "key_1"}, {"key": "key_2", "first_seen": "2023-07-17"}]
        source1 = Source(SOURCE_ID, metric=self.metric, entities=entities1)
        entities2 = [{"key": "key_1", "first_seen": "2023-07-18"}, {"key": "key_2", "first_seen": "2023-07-19"}]
        source2 = Source(SOURCE_ID, metric=self.metric, entities=entities2)
        source2.copy_entity_first_seen_timestamps(source1)
        self.assertEqual("2023-07-18", source2["entities"][0]["first_seen"])
        self.assertEqual("2023-07-17", source2["entities"][1]["first_seen"])


class SourceValueOfEntitiesToIgnoreTest(DataModelTestCase):
    """Test the value of the entities to ignore."""

    IGNORED_STATUSES = ("fixed", "false_positive", "wont_fix")
    NOT_IGNORED_STATUSES = ("unconfirmed", "confirmed")

    def setUp(self):
        """Set up date fixtures."""
        super().setUp()
        now = datetime.now(tz=tzutc())
        self.past = (now - timedelta(days=1)).isoformat()
        self.future = (now + timedelta(days=1)).isoformat()

    def source(self, source_type: str = "junit", metric_type: str = "tests", **kwargs) -> Source:
        """Create a source fixture, belonging to a metric of the specified metric type."""
        metric_data = {"type": metric_type, "sources": {SOURCE_ID: {"type": source_type}}}
        metric = Metric(self.DATA_MODEL, metric_data, METRIC_ID)
        return Source(SOURCE_ID, metric, {"source_uuid": SOURCE_ID, **kwargs})

    def source_with_one_entity(self, **entity_user_data) -> Source:
        """Create a source fixture with one entity, with the specified entity user data."""
        return self.source(entities=[{"key": "entity1"}], entity_user_data={"entity1": entity_user_data})

    def test_source_without_entities(self):
        """Test that the value is zero if the source has no entities."""
        self.assertEqual(0, self.source().value_of_entities_to_ignore())

    def test_entities_without_user_data(self):
        """Test that entities without user data are not ignored."""
        source = self.source(entities=[{"key": "entity1"}, {"key": "entity2"}])
        self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_ignored_statuses(self):
        """Test that entities marked as fixed, false positive, or won't fix are ignored."""
        for status in self.IGNORED_STATUSES:
            with self.subTest(status=status):
                source = self.source_with_one_entity(status=status)
                self.assertEqual(1, source.value_of_entities_to_ignore())

    def test_statuses_that_are_not_ignored(self):
        """Test that entities marked as unconfirmed or confirmed are not ignored."""
        for status in self.NOT_IGNORED_STATUSES:
            with self.subTest(status=status):
                source = self.source_with_one_entity(status=status)
                self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_status_end_date_in_the_future(self):
        """Test that entities with an ignored status are ignored as long as the status end date has not passed."""
        for status in self.IGNORED_STATUSES:
            with self.subTest(status=status):
                source = self.source_with_one_entity(status=status, status_end_date=self.future)
                self.assertEqual(1, source.value_of_entities_to_ignore())

    def test_status_end_date_in_the_past(self):
        """Test that entities with an ignored status are not ignored after the status end date has passed."""
        for status in self.IGNORED_STATUSES:
            with self.subTest(status=status):
                source = self.source_with_one_entity(status=status, status_end_date=self.past)
                self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_status_end_date_of_a_status_that_is_not_ignored(self):
        """Test that entities with a status that is not ignored are not ignored, whatever the status end date."""
        for status in self.NOT_IGNORED_STATUSES:
            for status_end_date in (self.past, self.future):
                with self.subTest(status=status, status_end_date=status_end_date):
                    source = self.source_with_one_entity(status=status, status_end_date=status_end_date)
                    self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_status_end_date_without_time_zone(self):
        """Test that status end dates without time zone information are compared with the local date and time."""
        for status_end_date, expected_value in (("2020-01-01", 0), ("3000-01-01", 1)):
            with self.subTest(status_end_date=status_end_date):
                source = self.source_with_one_entity(status="fixed", status_end_date=status_end_date)
                self.assertEqual(expected_value, source.value_of_entities_to_ignore())

    def test_empty_status_end_date(self):
        """Test that an empty status end date is ignored, and the entity is ignored based on its status only."""
        source = self.source_with_one_entity(status="fixed", status_end_date="")
        self.assertEqual(1, source.value_of_entities_to_ignore())

    def test_status_end_date_without_status(self):
        """Test that an entity with a status end date, but without status, is not ignored."""
        source = self.source_with_one_entity(status_end_date=self.future)
        self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_excluded_entities(self):
        """Test that excluded entities are ignored."""
        source = self.source_with_one_entity(excluded=True, exclusion_end_date=self.future)
        self.assertEqual(1, source.value_of_entities_to_ignore())

    def test_entities_that_are_not_excluded(self):
        """Test that the exclusion attributes take precedence over the status attributes."""
        source = self.source_with_one_entity(excluded=False, status="fixed", status_end_date=self.future)
        self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_user_data_of_entities_that_do_not_exist(self):
        """Test that user data of entities that are not in the measurement is ignored."""
        source = self.source(entities=[{"key": "entity1"}], entity_user_data={"entity2": {"status": "fixed"}})
        self.assertEqual(0, source.value_of_entities_to_ignore())

    def test_number_of_ignored_entities(self):
        """Test that the number of ignored entities is returned, if the entities have no measured attribute."""
        entities = [{"key": "entity1"}, {"key": "entity2"}, {"key": "entity3"}]
        entity_user_data = {
            "entity1": {"status": "fixed"},
            "entity2": {"status": "wont_fix"},
            "entity3": {"status": "confirmed"},
        }
        source = self.source(entities=entities, entity_user_data=entity_user_data)
        self.assertEqual(2, source.value_of_entities_to_ignore())

    def test_integer_measured_attribute(self):
        """Test that the measured attributes of the ignored entities are summed, if the entities have one."""
        entities = [
            {"key": "entity1", "counted_tests": 3},
            {"key": "entity2", "counted_tests": 5},
            {"key": "entity3", "counted_tests": 2},
        ]
        entity_user_data = {
            "entity1": {"status": "fixed"},
            "entity2": {"status": "wont_fix"},
            "entity3": {"status": "confirmed"},
        }
        source = self.source(source_type="azure_devops", entities=entities, entity_user_data=entity_user_data)
        self.assertEqual(8, source.value_of_entities_to_ignore())

    def test_measured_attribute_as_string(self):
        """Test that measured attributes are converted to their attribute type before being summed."""
        entities = [{"key": "entity1", "counted_tests": "3"}, {"key": "entity2", "counted_tests": "5"}]
        entity_user_data = {"entity1": {"status": "fixed"}, "entity2": {"status": "wont_fix"}}
        source = self.source(source_type="azure_devops", entities=entities, entity_user_data=entity_user_data)
        self.assertEqual(8, source.value_of_entities_to_ignore())

    def test_float_measured_attribute(self):
        """Test that the sum of float measured attributes is truncated to an integer."""
        entities = [{"key": "entity1", "points": 1.5}, {"key": "entity2", "points": 2.0}]
        entity_user_data = {"entity1": {"status": "fixed"}, "entity2": {"status": "wont_fix"}}
        source = self.source(
            source_type="jira",
            metric_type="user_story_points",
            entities=entities,
            entity_user_data=entity_user_data,
        )
        self.assertEqual(3, source.value_of_entities_to_ignore())
