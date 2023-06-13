"""Quality-time specific types."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, NewType, TypedDict

Color = Literal["blue", "green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
Scale = Literal["count", "percentage", "version_number"]
Status = Literal["informative", "target_met", "debt_target_met", "near_target_met", "target_not_met"]
TargetType = Literal["target", "near_target", "debt_target"]
SessionId = NewType("SessionId", str)
Value = str | None

ItemId = NewType("ItemId", str)
ReportId = NewType("ReportId", ItemId)
SubjectId = NewType("SubjectId", ItemId)
MetricId = NewType("MetricId", ItemId)
SourceId = NewType("SourceId", ItemId)
NotificationDestinationId = NewType("NotificationDestinationId", ItemId)


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
