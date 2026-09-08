"""Source model class."""

from typing import TYPE_CHECKING, cast

from .entity_user_data import EntityUserData

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
    def type(self) -> str:
        """Return the type of the source."""
        return str(self.get("type", "unknown"))

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

    def copy_entity_first_seen_timestamps(self, source: Source) -> None:  # pragma: no feature-test-cover
        """Copy the first seen timestamps of the source's entities to this source."""
        entities = {entity["key"]: entity for entity in self.get("entities", [])}
        for old_entity in source.get("entities", []):
            key = old_entity["key"]
            if key in entities and (first_seen := old_entity.get("first_seen")):
                entities[key]["first_seen"] = first_seen

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
        for entity_key, attributes in source.get("entity_user_data", {}).items():
            entity_key = changed_entity_keys.get(entity_key, entity_key)  # noqa: PLW2901
            entity_user_data = EntityUserData(attributes)
            entity_user_data.translate_legacy_attributes()
            if entity_key in new_entity_keys:
                entity_user_data.mark_not_orphaned()  # The entity reappeared
            elif entity_user_data.is_orphaned():
                if entity_user_data.orphaned_too_long():
                    continue  # Don't copy this user data, it has been orphaned too long
            else:
                # The entity user data refers to a disappeared entity. Keep it around in case the entity
                # returns, but also record the current date/time so we can eventually remove the user data.
                entity_user_data.mark_orphaned()
            self.setdefault("entity_user_data", {})[entity_key] = entity_user_data

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
        return [entity for entity in entities if EntityUserData(user_data.get(entity["key"], {})).is_ignored()]
