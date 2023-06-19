"""Session model class."""

from datetime import UTC, datetime

from utils.type import SessionData


class Session:
    """Class representing a user session."""

    def __init__(self, session_data: SessionData) -> None:
        self.__session_data = session_data or {}

    def is_valid(self) -> bool:
        """Return whether the session is valid."""
        expiration_datetime = self.__session_data.get("session_expiration_datetime", datetime.min)
        return bool(expiration_datetime.replace(tzinfo=UTC) > datetime.now(tz=UTC))

    def is_authorized(self, authorized_users: list[str]) -> bool:
        """Return whether the session's user is an authorized user."""
        if authorized_users:
            return bool({self.__session_data["user"], self.__session_data.get("email")} & set(authorized_users))
        return True
