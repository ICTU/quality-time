"""Base class for classes that handle (part of the) API-calls."""

from typing import Set, Type

import bottle


class API:
    """Base class for API-handlers."""

    subclasses: Set[Type["API"]] = set()

    def __init__(self, request: bottle.Request) -> None:
        self.request = request

    def __init_subclass__(cls, **kwargs):
        API.subclasses.add(cls)
        super().__init_subclass__(**kwargs)

    @classmethod
    def subclass_for_api(cls, api_name: str) -> Type["API"]:
        """Return the subclass registered for the API name."""
        match = lambda class_name, api_name: class_name.lower() == api_name.replace("_", "")
        try:
            return [subclass for subclass in API.subclasses if match(subclass.__name__, api_name)][0]
        except:
            print(api_name)
            raise
