"""Source model class."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.metric import Metric


class Source(dict):
    """Class representing a measurement source."""

    def __init__(self, metric: Metric, *args, **kwargs):
        self.__metric = metric
        super().__init__(*args, **kwargs)

    def total(self) -> int:
        """Return the measurement total of the source."""
        return int(self["total"])

    def value(self) -> int:
        """Return the measurement value of the source."""
        return int(self["value"]) - self._value_of_entities_to_ignore()

    def _value_of_entities_to_ignore(self) -> int:
        """Return the value of ignored entities, i.e. entities marked as fixed, false positive or won't fix.

        If the entities have a measured attribute, return the sum of the measured attributes of the ignored
        entities, otherwise return the number of ignored attributes. For example, if the metric is the amount of ready
        user story points, the source entities are user stories and the measured attribute is the amount of story
        points of each user story.
        """
        entities_to_ignore = self._entities_to_ignore()
        measured_attribute, attribute_type = self.__metric.get_measured_attribute(self)
        if measured_attribute:
            convert = dict(float=float, integer=int, minutes=int)[attribute_type]
            value = sum(convert(entity[measured_attribute]) for entity in entities_to_ignore)
        else:
            value = len(entities_to_ignore)
        return int(value)

    def _entities_to_ignore(self) -> Sequence[dict[str, str]]:
        """Return the entities to ignore."""
        statuses_to_ignore = ("fixed", "false_positive", "wont_fix")
        user_data = self.get("entity_user_data", {})
        entities = self.get("entities", [])
        return [entity for entity in entities if user_data.get(entity["key"], {}).get("status") in statuses_to_ignore]
