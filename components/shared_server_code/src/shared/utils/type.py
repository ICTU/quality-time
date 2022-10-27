"""Quality-time specific types."""

from collections import defaultdict
from dataclasses import dataclass, field

from typing import Literal, NewType, Optional


Color = Literal["blue", "green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
Scale = Literal["count", "percentage", "version_number"]
Status = Literal["informative", "target_met", "debt_target_met", "near_target_met", "target_not_met"]
TargetType = Literal["target", "near_target", "debt_target"]
SessionId = NewType("SessionId", str)
NotificationDestinationId = NewType("NotificationDestinationId", str)
Value = Optional[str]

ItemId = NewType("ItemId", str)
ReportId = NewType("ReportId", ItemId)
SubjectId = NewType("SubjectId", ItemId)
MetricId = NewType("MetricId", ItemId)
SourceId = NewType("SourceId", ItemId)


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

    def name_and_email(self) -> str:
        """Return the name of the user and their email, if any."""
        return f"{self.name()}" + (f" <{self.email}>" if self.email else "")

    def to_dict(self):
        """Return a dict representing this user."""
        return dict(username=self.username, email=self.email, common_name=self.common_name, settings=self.settings)
