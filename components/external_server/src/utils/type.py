"""Quality-time specific types."""

from dataclasses import dataclass
from typing import Literal, NewType, Union

from shared.utils.type import ReportId, SubjectId, MetricId, SourceId

Change = dict[str, Union[str, dict[str, str]]]
EditScope = Literal["source", "metric", "subject", "report", "reports"]
ItemId = Union[ReportId, SubjectId, MetricId, SourceId]
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

    def name(self) -> str:
        """Return the name of the user."""
        return self.common_name or self.username
