"""Measurement entity model class."""

from collections.abc import Sequence


class Entity(dict):
    """Class to hold information about an individual measurement entity, e.g. one violation, or one security warning."""

    def __init__(self, key: str, **attributes) -> None:
        kwargs = dict(key=self.safe_entity_key(key))
        kwargs.update(**attributes)
        super().__init__(**kwargs)

    @staticmethod
    def safe_entity_key(key: str) -> str:
        """Return a escaped version of the key that is safe in URLs and as Mongo document key."""
        return str(key).replace("/", "-").replace(".", "_")


Entities = Sequence[Entity]
