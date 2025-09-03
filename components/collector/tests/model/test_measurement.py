"""Unit tests for the SourceMeasurement model class."""

import unittest
from datetime import UTC, datetime

from shared.model.metric import Metric

from model.entity import Entities, Entity
from model.measurement import MetricMeasurement, SourceMeasurement

from tests.fixtures import METRIC_ID


class SourceMeasurementTest(unittest.TestCase):
    """Unit tests for the SourceMeasurement model class."""

    def create_entity(self, nr: int) -> Entity:
        """Create an entity fixture."""
        return Entity(key=str(nr), first_seen="2023-04-02", answer=42, end_of_time=datetime.max.replace(tzinfo=UTC))

    def test_entity_value_attributes(self):
        """Test that only Value type attributes are stored."""
        entities = Entities([self.create_entity(1)])
        measurement_dict = SourceMeasurement(entities=entities).as_dict()
        self.assertEqual([{"key": "1", "first_seen": "2023-04-02"}], measurement_dict["entities"])

    def test_limit_number_of_entities(self):
        """Test that the number of entities can be limited."""
        entities = Entities([self.create_entity(1), self.create_entity(2)])
        measurement_dict = SourceMeasurement(entities=entities).as_dict(max_entities=1)
        self.assertEqual([{"key": "1", "first_seen": "2023-04-02"}], measurement_dict["entities"])


class MetricMeasurementTest(unittest.TestCase):
    """Unit tests for the MetricMeasurement model class."""

    def test_default_max_entities(self):
        """Test the default maximum number of measurement entities to store."""
        metric = Metric({}, {"type": "violations"}, METRIC_ID)
        self.assertEqual(MetricMeasurement.DEFAULT_MAX_ENTITIES, MetricMeasurement(metric, [], []).max_entities)

    def test_security_warnings_max_entities(self):
        """Test that security warnings have no maximum number of entities stored."""
        metric = Metric({}, {"type": "security_warnings"}, METRIC_ID)
        self.assertIsNone(MetricMeasurement(metric, [], []).max_entities)
