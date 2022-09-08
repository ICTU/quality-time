"""Issue tracker."""

from dataclasses import asdict, dataclass
from typing import cast, Optional
import logging

import requests

from utils.type import URL


@dataclass
class IssueSuggestion:
    """Issue suggestion."""

    key: str
    text: str

    def as_dict(self) -> dict[str, str]:
        """Convert issue suggestion to dict."""
        return asdict(self)  # pragma: no cover behave


@dataclass
class IssueTrackerCredentials:
    """Issue tracker credentials needed to create issues."""

    username: str = ""
    password: str = ""
    private_token: str = ""

    def basic_auth_credentials(self) -> tuple[str, str] | None:
        """Return the basic authentication credentials, if any."""
        return (self.username, self.password) if self.username or self.password else None

    def auth_headers(self) -> dict[str, str]:
        """Return the authorization headers, if any."""
        return dict(Authorization=f"Bearer {self.private_token}") if self.private_token else {}


@dataclass
class IssueParameters:
    """Parameters to create issues with."""

    project_key: str
    issue_type: str
    issue_labels: Optional[list[str]] = None


JiraIssueSuggestionJSON = dict[str, list[dict[str, str | dict[str, str]]]]


@dataclass
class IssueTracker:
    """Issue tracker. Only supports Jira at the moment."""

    url: URL
    issue_parameters: IssueParameters
    credentials: IssueTrackerCredentials = IssueTrackerCredentials()
    issue_creation_api = "%s/rest/api/2/issue"
    issue_browse_url = "%s/browse/%s"
    suggestions_api: str = "%s/rest/api/2/search?jql=summary~'%s~10' order by updated desc&fields=summary&maxResults=20"

    def create_issue(self, summary: str, description: str = "") -> tuple[str, str]:
        """Create a new issue and return its key or an error message if creating the issue failed."""
        for attribute, name in [
            (self.url, "URL"),
            (self.issue_parameters.project_key, "project key"),
            (self.issue_parameters.issue_type, "issue type"),
        ]:
            if not attribute:
                return "", f"Issue tracker has no {name} configured."
        api_url = self.issue_creation_api % (self.url.rstrip("/"))
        json = dict(
            fields=dict(
                project=dict(key=self.issue_parameters.project_key),
                issuetype=dict(name=self.issue_parameters.issue_type),
                summary=summary,
                description=description,
                labels=self.issue_parameters.issue_labels or [],
            )
        )
        try:
            response = requests.post(
                api_url,
                auth=self.credentials.basic_auth_credentials(),
                headers=self.credentials.auth_headers(),
                json=json,
            )
            response.raise_for_status()  # pragma: no cover behave
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Creating a new issue at %s failed: %s", api_url, reason)
            return "", str(reason)
        return response.json()["key"], ""  # pragma: no cover behave

    def get_suggestions(self, query: str) -> list[IssueSuggestion]:
        """Get a list of issue id suggestions based on the query string."""
        api_url = self.suggestions_api % (self.url.rstrip("/"), query)
        try:
            response = requests.get(
                api_url, auth=self.credentials.basic_auth_credentials(), headers=self.credentials.auth_headers()
            )
            response.raise_for_status()  # pragma: no cover behave
            json = response.json()  # pragma: no cover behave
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Retrieving issue id suggestions from %s failed: %s", api_url, reason)
            return []
        return self._parse_suggestions(json)  # pragma: no cover behave

    def browse_url(self, issue_key: str) -> URL:
        """Return a URL to a human readable version of the issue."""
        return URL(self.issue_browse_url % (self.url.rstrip("/"), issue_key))  # pragma: no cover behave

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no cover behave
        """Parse the suggestions from the JSON."""
        issues = json.get("issues", [])
        return [IssueSuggestion(str(issue["key"]), cast(dict, issue["fields"])["summary"]) for issue in issues]
