"""Issue tracker."""

from dataclasses import asdict, dataclass
from typing import cast
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


JiraIssueSuggestionJSON = dict[str, list[dict[str, str | dict[str, str]]]]


@dataclass
class IssueTracker:
    """Issue tracker. Only supports Jira at the moment."""

    url: URL
    username: str = ""
    password: str = ""
    private_token: str = ""
    project_key: str = ""
    issue_type: str = ""
    issue_creation_api = "%s/rest/api/2/issue"
    issue_browse_url = "%s/browse/%s"
    suggestions_api: str = "%s/rest/api/2/search?jql=summary~'%s~10' order by updated desc&fields=summary&maxResults=20"

    def create_issue(self, summary: str) -> tuple[str, str]:
        """Create a new issue and return its key or an error message if creating the issue failed."""
        api_url = self.issue_creation_api % (self.url.rstrip("/"))
        issue_fields = dict(project=dict(key=self.project_key), issuetype=dict(name=self.issue_type), summary=summary)
        json = dict(fields=issue_fields)
        try:
            response = requests.post(
                api_url, auth=self._basic_auth_credentials(), headers=self._auth_headers(), json=json
            )
            response.raise_for_status()
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Creating a new issue at %s failed: %s", api_url, reason)
            return "", str(reason)
        return response.json()["key"], ""

    def get_suggestions(self, query: str) -> list[IssueSuggestion]:
        """Get a list of issue id suggestions based on the query string."""
        api_url = self.suggestions_api % (self.url.rstrip("/"), query)
        try:
            response = requests.get(api_url, auth=self._basic_auth_credentials(), headers=self._auth_headers())
            # pragma: no cover behave
            response.raise_for_status()
            json = response.json()
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Retrieving issue id suggestions from %s failed: %s", api_url, reason)
            return []
        return self._parse_suggestions(json)  # pragma: no cover behave

    def browse_url(self, issue_key: str) -> URL:
        """Return a URL to a human readable version of the issue."""
        return URL(self.issue_browse_url % (self.url.rstrip("/"), issue_key))

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no cover behave
        """Parse the suggestions from the JSON."""
        issues = json.get("issues", [])
        return [IssueSuggestion(str(issue["key"]), cast(dict, issue["fields"])["summary"]) for issue in issues]

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Return the basic authentication credentials, if any."""
        return (self.username, self.password) if self.username or self.password else None

    def _auth_headers(self) -> dict[str, str]:
        """Return the authorization headers, if any."""
        return dict(Authorization=f"Bearer {self.private_token}") if self.private_token else {}
