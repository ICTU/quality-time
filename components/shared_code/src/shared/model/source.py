"""Source model class."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast

from shared.utils.functions import iso_timestamp

if TYPE_CHECKING:
    from collections.abc import Sequence

    from shared.utils.type import SourceId

    from .metric import Metric


class Source(dict):
    """Class representing a measurement source."""

    def __init__(self, source_uuid: SourceId, metric: Metric, *args, **kwargs) -> None:
        self.metric = metric
        self.uuid = source_uuid
        super().__init__(*args, **kwargs)

    @property
    def type(self) -> str | None:  # noqa: A003
        """Return the type of the source."""
        return str(self["type"]) if "type" in self else None

    @property
    def name(self) -> str | None:
        """Easier way to access name."""
        return self.get("name")

    def total(self) -> str | None:
        """Return the measurement total of the source."""
        return cast(str | None, self["total"])

    def value(self) -> str | None:
        """Return the measurement value of the source."""
        return cast(str | None, self["value"])

    def copy_entity_user_data(self, source: Source) -> None:  # pragma: no feature-test-cover
        """Copy the user entity data of the source to this source."""
        new_entity_keys = {entity["key"] for entity in self.get("entities", [])}
        # Sometimes the key Quality-time generates for entities needs to change, e.g. when it turns out not to be
        # unique. Create a mapping of old keys to new keys so we can move the entity user data to the new keys
        changed_entity_keys = {
            entity["old_key"]: entity["key"] for entity in self.get("entities", []) if "old_key" in entity
        }
        # Copy the user data of entities, keeping 'orphaned' entity user data around for a while in case the entity
        # returns in a later measurement:
        max_timedelta_to_keep_orphaned_entity_user_data = timedelta(days=21)
        for entity_key, attributes in source.get("entity_user_data", {}).items():
            entity_key = changed_entity_keys.get(entity_key, entity_key)  # noqa: PLW2901
            if entity_key in new_entity_keys:
                if "orphaned_since" in attributes:
                    del attributes["orphaned_since"]  # The entity reappeared, remove the orphaned since date/time
            elif "orphaned_since" in attributes:
                orphaned_since = datetime.fromisoformat(attributes["orphaned_since"])
                orphaned_timedelta = datetime.now(tz=orphaned_since.tzinfo) - orphaned_since
                if orphaned_timedelta > max_timedelta_to_keep_orphaned_entity_user_data:
                    continue  # Don't copy this user data, it has been orphaned too long
            else:
                # The entity user data refers to a disappeared entity. Keep it around in case the entity
                # returns, but also set the current date/time so we can eventually remove the user data.
                attributes["orphaned_since"] = iso_timestamp()
            self.setdefault("entity_user_data", {})[entity_key] = attributes

    def value_of_entities_to_ignore(self) -> int:
        """Return the value of ignored entities, i.e. entities marked as fixed, false positive or won't fix.

        If the entities have a measured attribute, return the sum of the measured attributes of the ignored
        entities, otherwise return the number of ignored attributes. For example, if the metric is the number of ready
        user story points, the source entities are user stories and the measured attribute is the number of story
        points of each user story.
        """
        entities_to_ignore = self._entities_to_ignore()
        measured_attribute, attribute_type = self.metric.get_measured_attribute(self)
        if measured_attribute:
            convert = {"float": float, "integer": int, "minutes": int}[attribute_type]
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
    def _entity_to_be_ignored(entity: dict[str, str]) -> bool:
        """Return whether to ignore the entity."""
        statuses_to_ignore = ("fixed", "false_positive", "wont_fix")
        status_end_date = entity.get("status_end_date")
        if status_end_date:
            status_end_datetime = datetime.fromisoformat(status_end_date)
            if status_end_datetime < datetime.now(tz=status_end_datetime.tzinfo):
                return False
        return entity.get("status") in statuses_to_ignore
