"""Issue status model class."""

from dataclasses import dataclass
from typing import Literal

from collector_utilities.type import ErrorMessage, URL


@dataclass
class IssueSprint:
    """Class representing a sprint of which an issue is part."""

    name: str | None = None
    state: str | None = None
    enddate: str | None = None

    def as_dict(self) -> dict:
        """Return the sprint as dict."""
        return dict(
            sprint_name=self.name,
            sprint_state=self.state,
            sprint_enddate=self.enddate,
        )


@dataclass
class IssueRelease:
    """Class representing a release of which an issue is part."""

    name: str | None = None
    released: bool | None = None
    date: str | None = None

    def as_dict(self) -> dict:
        """Return the release as dict."""
        return dict(
            release_name=self.name,
            release_released=self.released,
            release_date=self.date,
        )


@dataclass
class Issue:
    """Class representing issues."""

    name: str | None = None
    summary: str | None = None
    created: str | None = None
    updated: str | None = None
    duedate: str | None = None
    release: IssueRelease | None = None
    sprint: IssueSprint | None = None

    def as_dict(self) -> dict:
        """Return the issue as dict."""
        return dict(
            name=self.name,
            summary=self.summary,
            created=self.created,
            updated=self.updated,
            duedate=self.duedate,
            **(self.release.as_dict() if self.release else {}),
            **(self.sprint.as_dict() if self.sprint else {}),
        )


IssueStatusCategory = Literal["todo", "doing", "done"]


class IssueStatus:  # pylint: disable=too-few-public-methods
    """Class to hold the status of issues."""

    def __init__(
        self,
        issue_id: str,
        *,
        issue: Issue | None = None,
        status_category: IssueStatusCategory | None = None,
        connection_error: ErrorMessage | None = None,
        parse_error: ErrorMessage | None = None
    ) -> None:
        self.issue_id = issue_id
        self.issue = issue or Issue()
        self.status_category = status_category
        self.parse_error = parse_error
        self.connection_error = connection_error
        self.api_url: URL | None = None
        self.landing_url: URL | None = None

    def as_dict(self) -> dict:
        """Return the issue status as dict."""
        status = dict(
            issue_id=self.issue_id,
            status_category=self.status_category,
            parse_error=self.parse_error,
            connection_error=self.connection_error,
            api_url=self.api_url,
            landing_url=self.landing_url,
            **self.issue.as_dict(),
        )
        return {key: value for key, value in status.items() if value is not None}
