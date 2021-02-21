"""Session model class."""

from datetime import datetime, timezone
from typing import Union, cast


class Session:
    """Class representing a user session."""

    def __init__(self, session_data: dict[str, Union[datetime, str]]) -> None:
        self.__session_data = session_data or {}

    def is_valid(self) -> bool:
        """Return whether the session is valid."""
        expiration_datetime = cast(
            datetime, self.__session_data.get("session_expiration_datetime", datetime.min.replace(tzinfo=timezone.utc))
        )
        return bool(expiration_datetime > datetime.now(timezone.utc))

    def is_authorized(self, authorized_users: list[str]) -> bool:
        """Return whether the session's user is an authorized user."""
        if authorized_users:
            return bool({self.__session_data["user"], self.__session_data.get("email")} & set(authorized_users))
        return True
