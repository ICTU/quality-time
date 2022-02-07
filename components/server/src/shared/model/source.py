"""Source model class."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import cast, Optional, TYPE_CHECKING

from shared.utils.functions import days_ago, iso_timestamp


if TYPE_CHECKING:
    from .metric import Metric


class Source(dict):  # lgtm [py/missing-equals]
    """Class representing a measurement source."""

    # LGTM wants us to implement __eq__ because this class has metric as instance attribute. However, the source
    # dictionary contains the source UUID and thus we don't need to compare the metrics to know whether two sources
    # are the same.

    def __init__(self, metric: Metric, *args, **kwargs):
        self.__metric = metric
        super().__init__(*args, **kwargs)

    def total(self) -> str | None:
        """Return the measurement total of the source."""
        return cast(Optional[str], self["total"])

    def value(self) -> str | None:
        """Return the measurement value of the source."""
        return cast(Optional[str], self["value"])

    def copy_entity_user_data(self, source: Source) -> None:
        """Copy the user entity data of the source to this source."""
        new_entity_keys = {entity["key"] for entity in self.get("entities", [])}
        # Sometimes the key Quality-time generates for entities needs to change, e.g. when it turns out not to be
        # unique. Create a mapping of old keys to new keys so we can move the entity user data to the new keys
        changed_entity_keys = {
            entity["old_key"]: entity["key"] for entity in self.get("entities", []) if "old_key" in entity
        }
        # Copy the user data of entities, keeping 'orphaned' entity user data around for a while in case the entity
        # returns in a later measurement:
        max_days_to_keep_orphaned_entity_user_data = 21
        for entity_key, attributes in source.get("entity_user_data", {}).items():
            entity_key = changed_entity_keys.get(entity_key, entity_key)
            if entity_key in new_entity_keys:
                if "orphaned_since" in attributes:
                    del attributes["orphaned_since"]  # The entity returned, remove the orphaned since date/time
            else:
                if "orphaned_since" in attributes:
                    days_since_orphaned = days_ago(datetime.fromisoformat(attributes["orphaned_since"]))
                    if days_since_orphaned > max_days_to_keep_orphaned_entity_user_data:  # pragma: no cover-behave
                        continue  # Don't copy this user data, it has been orphaned too long
                else:
                    # The entity user data refers to a disappeared entity. Keep it around in case the entity
                    # returns, but also set the current date/time so we can eventually remove the user data.
                    attributes["orphaned_since"] = iso_timestamp()
            self.setdefault("entity_user_data", {})[entity_key] = attributes

    def value_of_entities_to_ignore(self) -> int:
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
        user_data = self.get("entity_user_data", {})
        entities = self.get("entities", [])
        return [entity for entity in entities if self._entity_to_be_ignored(user_data.get(entity["key"], {}))]

    @staticmethod
    def _entity_to_be_ignored(entity) -> bool:
        """Return whether to ignore the entity."""
        statuses_to_ignore = ("fixed", "false_positive", "wont_fix")
        if status_end_date := entity.get("status_end_date"):
            if datetime.fromisoformat(status_end_date) < datetime.now():
                return False
        return entity.get("status") in statuses_to_ignore
