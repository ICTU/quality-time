"""Issue status model class."""

from typing import Optional

from collector_utilities.type import ErrorMessage, URL


class IssueStatus:  # pylint: disable=too-few-public-methods
    """Class to hold the status of issues."""

    def __init__(
        self,
        issue_id: str,
        *,
        name: str = None,
        created: str = None,
        connection_error: ErrorMessage = None,
        parse_error: ErrorMessage = None
    ) -> None:
        self.issue_id = issue_id
        self.name = name
        self.parse_error = parse_error
        self.connection_error = connection_error
        self.created = created
        self.api_url: Optional[URL] = None
        self.landing_url: Optional[URL] = None

    def as_dict(self) -> dict:
        """Return the issue status as dict."""
        status = dict(
            issue_id=self.issue_id,
            name=self.name,
            parse_error=self.parse_error,
            connection_error=self.connection_error,
            created=self.created,
            api_url=self.api_url,
            landing_url=self.landing_url,
        )
        return {key: value for key, value in status.items() if value}
