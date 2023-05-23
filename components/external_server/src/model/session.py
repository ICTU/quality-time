"""Session model class."""

from datetime import datetime, UTC
from typing import cast

from shared.utils.type import User


class Session:
    """Class representing a user session."""

    def __init__(self, session_data: dict[str, datetime | str]) -> None:
        self.__session_data = session_data or {}

    def is_valid(self) -> bool:
        """Return whether the session is valid."""
        expiration_datetime = cast(datetime, self.__session_data.get("session_expiration_datetime", datetime.min))
        return bool(expiration_datetime.replace(tzinfo=UTC) > datetime.now(tz=UTC))

    def is_authorized(self, authorized_users: list[str]) -> bool:
        """Return whether the session's user is an authorized user."""
        if authorized_users:
            return bool({self.__session_data["user"], self.__session_data.get("email")} & set(authorized_users))
        return True

    def user(self) -> User:
        """Return the session's user."""
        return User(
            str(self.__session_data["user"]),
            str(self.__session_data.get("email", "")),
            str(self.__session_data.get("common_name", "")),
        )
