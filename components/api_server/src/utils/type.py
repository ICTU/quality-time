"""Quality-time specific types."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, NewType, TypedDict

Change = dict[str, str | dict[str, str]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
Position = Literal["first", "last", "next", "previous"]
SessionId = NewType("SessionId", str)
URL = NewType("URL", str)


@dataclass
class User:
    """Class representing a user."""

    username: str
    email: str = ""
    common_name: str = ""
    verified: bool = False
    # use a defaultdict to prevent a mutable default
    settings: defaultdict = field(default_factory=lambda: defaultdict(dict))

    def name(self) -> str:
        """Return the name of the user."""
        return self.common_name or self.username

    def to_dict(self) -> dict[str, str | dict]:
        """Return a dict representing this user."""
        return {
            "username": self.username,
            "email": self.email,
            "common_name": self.common_name,
            "settings": self.settings,
        }


class SessionData(TypedDict, total=False):
    """Session data as stored in the database."""

    user: str
    email: str
    common_name: str
    session_expiration_datetime: datetime
