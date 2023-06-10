"""Test the source model."""

import unittest
from datetime import UTC, datetime, timedelta

from shared.model.source import Source

from tests.fixtures import SOURCE_ID


class SourceTest(unittest.TestCase):
    """Test the source model."""

    def test_copy_entity_user_data(self):
        """Test copy entity user data."""
        now = datetime.now(tz=UTC).isoformat()
        long_ago = (datetime.now(tz=UTC) - timedelta(days=30)).isoformat()
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
