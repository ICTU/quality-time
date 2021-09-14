"""Issue status model class."""

from typing import Optional

from collector_utilities.type import ErrorMessage, URL


class IssueStatus:  # pylint: disable=too-few-public-methods
    """Class to hold the status of issues."""

    def __init__(self, issue: str, *, name: str = None, description: str = None, parse_error: str = None) -> None:
        self.issue = issue
        self.name = name
        self.description = description
        self.parse_error = parse_error
        self.connection_error: ErrorMessage = None
        self.api_url: Optional[URL] = None
        self.landing_url: Optional[URL] = None

    def as_dict(self) -> dict:
        """Return the issue status as dict."""
        return dict(
            name=self.name,
            description=self.description,
            parse_error=self.parse_error,
            connection_error=self.connection_error,
            api_url=self.api_url,
            landing_url=self.landing_url,
        )
