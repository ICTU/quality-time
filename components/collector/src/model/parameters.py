"""Source parameters."""

from typing import cast
import urllib

from shared_data_model import DATA_MODEL

from collector_utilities.type import URL


class SourceParameters:
    """Source parameters."""

    def __init__(self, source: dict) -> None:
        self.__source = source
        self.__parameters = source.get("parameters", {})

    def api_url(self) -> URL:
        """Return the API URL."""
        return URL(cast(str, self.__parameters.get("url", "")).rstrip("/"))

    def landing_url(self) -> URL:
        """Return the human friendly landing URL."""
        return URL(cast(str, self.__parameters.get("landing_url", "")).rstrip("/"))

    def private_token(self) -> str:
        """Return the private token."""
        return cast(str, self.__parameters.get("private_token", ""))

    def username(self) -> str:
        """Return the username."""
        return cast(str, self.__parameters.get("username", ""))

    def password(self) -> str:
        """Return the password."""
        return cast(str, self.__parameters.get("password", ""))

    def get(self, parameter_key: str, quote: bool = False) -> str | list[str]:
        """Return the parameter with the given key."""

        def quote_if_needed(parameter_value: str) -> str:
            """Quote the string if needed."""
            return urllib.parse.quote(parameter_value, safe="") if quote else parameter_value

        parameter_info = DATA_MODEL.sources[self.__source["type"]].parameters[parameter_key]
        if parameter_info.type == "multiple_choice":
            # If the user didn't pick any values, select the default value if any, otherwise select all values:
            default_value = parameter_info.default_value
            value = self.__parameters.get(parameter_key) or default_value or parameter_info.values or []
            # Ensure all values picked by the user are still allowed. Remove any values that are no longer allowed:
            value = [v for v in value if v in (parameter_info.values or [])]
        else:
            default_value = parameter_info.default_value
            value = self.__parameters.get(parameter_key) or default_value
        if api_values := parameter_info.api_values:
            value = api_values.get(value, value) if isinstance(value, str) else [api_values.get(v, v) for v in value]
        if parameter_key.endswith("url"):
            value = cast(str, value).rstrip("/")
        return quote_if_needed(value) if isinstance(value, str) else [quote_if_needed(v) for v in value]
