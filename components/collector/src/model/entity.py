"""Measurement entity model class."""

import re
from collections.abc import Iterable

from shared.utils.functions import iso_timestamp

QUOTED_SLASH = re.compile("%2f", re.IGNORECASE)


class Entity(dict):
    """Class to hold information about an individual measurement entity, e.g. one violation, or one security warning."""

    def __init__(self, key: str, **attributes) -> None:
        kwargs = {"key": self.safe_entity_key(key), "first_seen": iso_timestamp()}
        kwargs.update(**attributes)
        super().__init__(**kwargs)

    @staticmethod
    def safe_entity_key(key: str) -> str:
        """Return an escaped version of the key that is safe in URLs and as Mongo document key."""
        return re.sub(QUOTED_SLASH, "-", str(key).replace("/", "-").replace(".", "_"))


class Entities(list[Entity]):
    """Class to hold a list of unique entities."""

    def __init__(self, entities: Iterable[Entity] = ()) -> None:
        """Override to filter duplicate entities."""
        self.__keys: set[str] = set()  # Keep track of the keys in a set to make adding entities faster
        self.extend(entities)

    def __add__(self, other):
        """Return the concatenation of the entities."""
        return self.__class__(super().__add__(other))

    def __getitem__(self, item):
        """Override to return an Entities slice or an Entity."""
        return self.__class__(super().__getitem__(item)) if isinstance(item, slice) else super().__getitem__(item)

    def append(self, entity: Entity) -> None:
        """Extend to only append the entity if it's not already in the list."""
        if (key := entity["key"]) not in self.__keys:
            self.__keys.add(key)
            super().append(entity)

    def extend(self, entities: Iterable[Entity]) -> None:
        """Extend to only add entities that aren't already in the list."""
        for entity in entities:
            self.append(entity)  # noqa: PERF402
