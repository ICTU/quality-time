"""Source model class."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, TYPE_CHECKING

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

    def value(self, measured_attribute: Optional[str], attribute_type: str) -> int:
        """Return the measurement value of the source."""
        return int(self["value"]) - self._value_of_entities_to_ignore(measured_attribute, attribute_type)

    def _value_of_entities_to_ignore(self, measured_attribute: Optional[str], attribute_type: str) -> int:
        """Return the value of ignored entities, i.e. entities marked as fixed, false positive or won't fix.

        If the entities have a measured attribute, return the sum of the measured attributes of the ignored
        entities, otherwise return the number of ignored attributes. For example, if the metric is the amount of ready
        user story points, the source entities are user stories and the measured attribute is the amount of story
        points of each user story.
        """
        ignored_entity_keys = self._ignored_entity_keys()
        if measured_attribute:
            convert = dict(float=float, integer=int, minutes=int)[attribute_type]
            value = sum(
                convert(entity[measured_attribute])
                for entity in self["entities"]
                if entity["key"] in ignored_entity_keys
            )
        else:
            value = len(ignored_entity_keys)
        return int(value)

    def _ignored_entity_keys(self) -> Sequence[str]:
        """Return the keys of the ignored entities."""
        entities = self.get("entity_user_data", {}).items()
        return [entity[0] for entity in entities if entity[1].get("status") in ("fixed", "false_positive", "wont_fix")]
