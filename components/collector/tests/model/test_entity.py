"""Unit tests for the entity model class."""

import unittest

from model.entity import Entity, Entities


class EntityTest(unittest.TestCase):
    """Unit tests for the entity model class."""

    def test_init_with_duplicate_entities(self):
        """Test that duplicate entities are removed on initialization."""
        entities = Entities([Entity(key="1"), Entity(key="2"), Entity(key="2")])
        self.assertEqual(2, len(entities))

    def test_entity_key(self):
        """Test that unsafe characters are replaced."""
        self.assertEqual("_", Entity(".")["key"])
        self.assertEqual("-", Entity("/")["key"])
        self.assertEqual("-", Entity(r"%2f")["key"])
        self.assertEqual("-", Entity(r"%2F")["key"])
