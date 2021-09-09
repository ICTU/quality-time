"""Module to hold class to represent a tracked Issue."""

from typing import Optional


class TrackerIssueStatus:
    """Class to represent a tracked Issue."""

    def __init__(  # pylint: disable=too-many-arguments
        self, name: Optional[str], description: str = None, landing_url: str = None, error_message: str = None
    ):
        """Initialize this tracked Issue."""
        self.name = name
        self.description = description
        self.landing_url = landing_url
        self.error_message = error_message

    @classmethod
    def empty_status(cls) -> "TrackerIssueStatus":
        """Instantiate an error."""
        return cls(name=None)

    @classmethod
    def connection_error(cls, message: str) -> "TrackerIssueStatus":
        """Instantiate an error."""
        return cls(name="Connection error", error_message=message)

    @classmethod
    def parse_error(cls, message: str) -> "TrackerIssueStatus":
        """Instantiate an error."""
        return cls(name="Parse error", error_message=message)

    def to_dict(self) -> dict:
        """For sending this tracker issue status to the frontend."""
        return dict(
            name=self.name,
            description=self.description,
            landing_url=self.landing_url,
            error_message=self.error_message,
        )
