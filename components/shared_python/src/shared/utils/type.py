"""Quality-time specific types."""

from dataclasses import dataclass

from typing import Literal, NewType


Color = Literal["green", "grey", "red", "yellow", "white"]
Direction = Literal["<", ">"]
Scale = Literal["count", "percentage", "version_number"]
Status = Literal["target_met", "debt_target_met", "near_target_met", "target_not_met"]
TargetType = Literal["target", "near_target", "debt_target"]
SessionId = NewType("SessionId", str)


ReportId = NewType("ReportId", str)
SubjectId = NewType("SubjectId", str)
MetricId = NewType("MetricId", str)
SourceId = NewType("SourceId", str)


@dataclass
class User:
    """Class representing a user."""

    username: str
    email: str = ""
    common_name: str = ""
    verified: bool = False

    def name(self) -> str:
        """Return the name of the user."""
        return self.common_name or self.username
