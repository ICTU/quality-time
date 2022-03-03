"""Test the Metric model."""

from datetime import datetime
import unittest

from shared.model.source import Source


class SourceTest(unittest.TestCase):
    """Test the Source model."""

    def test_copy_entity_user_data(self):
        """Test copy entity user data."""
        now = str(datetime.now().isoformat())
        old_eud = {
            "key_1": {"orphaned_since": now},
            "key_2": {"orphaned_since": now},
            "key_3": {},
        }

        old_source = Source(metric=None, entity_user_data=old_eud)

        new_entities = [{"key": "key_2"}, {"key": "key_3"}]

        new_source = Source(metric=None, entities=new_entities)

        new_source.copy_entity_user_data(old_source)

        self.assertIn("entity_user_data", new_source)
        self.assertIn("key_1", new_source["entity_user_data"])
        self.assertIn("key_2", new_source["entity_user_data"])
        self.assertIn("key_3", new_source["entity_user_data"])
        self.assertNotIn("orphaned_since", new_source["entity_user_data"]["key_2"])
