"""Base class for classes that handle (part of the) API-calls."""

from typing import Mapping, Set, Type

from .type import MeasurementResponse


class API:
    """Base class for API-handlers."""

    subclasses: Set[Type["API"]] = set()

    def __init__(self, query: Mapping[str, str]) -> None:
        self.query = query

    def __init_subclass__(cls, **kwargs):
        API.subclasses.add(cls)
        super().__init_subclass__(**kwargs)

    @classmethod
    def subclass_for_api(cls, api_name: str) -> Type["API"]:
        """Return the subclass registered for the API name."""
        simplified_api_name = api_name.replace("_", "")
        matching_subclasses = [sc for sc in API.subclasses if sc.__name__.lower() == simplified_api_name]
        return matching_subclasses[0] if matching_subclasses else UnknownAPI


class UnknownAPI(API):
    """Handle unknown APIs."""

    def get(self, *args, **kwargs) -> MeasurementResponse:  # pylint: disable=unused-argument
        """Return an error message."""
        return dict(request_error=f"Unknown <metric>/<source>")
