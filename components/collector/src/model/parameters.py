"""Source parameters."""

from typing import cast

from collector_utilities.type import URL


class SourceParameters:
    """Source parameters."""

    def __init__(self, source: dict, api_url_parameter_key: str) -> None:
        self.__parameters = source.get("parameters", {})
        self.__api_url_parameter_key = api_url_parameter_key

    def api_url(self) -> URL:
        """Return the API URL."""
        return URL(cast(str, self.__parameters.get(self.__api_url_parameter_key, "")).rstrip("/"))

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

    def get(self, parameter_key: str):
        """Return the parameter with the given key."""
        return self.__parameters.get(parameter_key)
