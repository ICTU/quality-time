"""Base class for classes that handle (part of the) API-calls."""

from typing import Type


class API:
    """Base class for API-handlers."""

    @classmethod
    def subclass_for_api(cls, api_name: str) -> Type["API"]:
        """Return the subclass registered for the API name."""
        match = lambda class_name, api_name: class_name.lower() == api_name.replace("_", "")
        return [subclass for subclass in cls.__subclasses__() if match(subclass.__name__, api_name)][0]

    @classmethod
    def name(cls) -> str:
        """Return the name of the API."""
        return cls.__name__
