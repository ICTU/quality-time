"""Session model class."""

from datetime import datetime
from typing import List


class Session:
    """Class representing a user session."""

    def __init__(self, session_data):
        self.__session_data = session_data

    def is_valid(self) -> bool:
        """Return whether the session is valid."""
        if self.__session_data:
            return bool(self.__session_data.get("session_expiration_datetime", datetime.min) > datetime.now())
        return False  # No session exists

    def is_authorized(self, authorized_users: List[str]) -> bool:
        """Return whether the session's user is an authorized user."""
        if authorized_users:
            return self.__session_data["email"] in authorized_users
        return True  # No authorized users specified, so any (logged in) user is authorized
