"""Issue status model class."""

from dataclasses import dataclass
from typing import Literal

from collector_utilities.type import ErrorMessage, URL


@dataclass
class Issue:
    """Class representing issues."""

    issue_id: str
    name: str | None = None
    summary: str | None = None
    created: str | None = None
    updated: str | None = None

    def as_dict(self) -> dict:
        """Return the issue as dict."""
        return dict(
            issue_id=self.issue_id, name=self.name, summary=self.summary, created=self.created, updated=self.updated
        )


IssueStatusCategory = Literal["todo", "doing", "done"]


class IssueStatus:  # pylint: disable=too-few-public-methods
    """Class to hold the status of issues."""

    def __init__(
        self,
        issue_id: str,
        *,
        name: str = None,
        status_category: IssueStatusCategory = None,
        created: str = None,
        updated: str = None,
        summary: str = None,
        connection_error: ErrorMessage = None,
        parse_error: ErrorMessage = None
    ) -> None:
        self.issue = Issue(issue_id, name, summary, created, updated)
        self.status_category = status_category
        self.parse_error = parse_error
        self.connection_error = connection_error
        self.api_url: URL | None = None
        self.landing_url: URL | None = None

    def as_dict(self) -> dict:
        """Return the issue status as dict."""
        status = dict(
            status_category=self.status_category,
            parse_error=self.parse_error,
            connection_error=self.connection_error,
            api_url=self.api_url,
            landing_url=self.landing_url,
            **self.issue.as_dict(),
        )
        return {key: value for key, value in status.items() if value is not None}
