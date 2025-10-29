"""Unit tests for the SourceMeasurement model class."""

import unittest
from datetime import datetime

from dateutil.tz import tzutc

from model.entity import Entities, Entity
from model.measurement import SourceMeasurement


class SourceMeasurementTest(unittest.TestCase):
    """Unit tests for the SourceMeasurement model class."""

    def test_entity_value_attributes(self):
        """Test that only Value type attributes are stored."""
        entities = Entities(
            [Entity(key="1", first_seen="2023-04-02", answer=42, end_of_time=datetime.max.replace(tzinfo=tzutc()))]
        )
        measurement_dict = SourceMeasurement(entities=entities).as_dict()
        self.assertEqual([{"key": "1", "first_seen": "2023-04-02"}], measurement_dict["entities"])
