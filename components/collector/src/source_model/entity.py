"""Measurement entity model class."""


from collector_utilities.functions import safe_entity_key


class Entity(dict):
    """Class to hold information about an individual measurement entity, e.g. one violation, or one security warning."""
    def __init__(self, key, **attributes) -> None:
        kwargs = dict(key=safe_entity_key(key))
        kwargs.update(**attributes)
        super().__init__(**kwargs)
