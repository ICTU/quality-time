"""Issue tracker."""

from dataclasses import asdict, dataclass
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


JiraIssueSuggestionJSON = dict[str, list[dict[str, list[dict[str, str]]]]]


@dataclass
class IssueTracker:
    """Issue tracker. Only supports Jira at the moment."""

    url: URL
    username: str = ""
    password: str = ""
    private_token: str = ""
    suggestions_api: str = "/rest/api/2/issue/picker?query="

    def get_suggestions(self, query: str) -> list[IssueSuggestion]:
        """Get a list of issue id suggestions based on the query string."""
        api_url = self.url.rstrip("/") + self.suggestions_api + query
        try:
            response = requests.get(api_url, auth=self._basic_auth_credentials(), headers=self._auth_headers())
            json = response.json()  # pragma: no cover behave
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Retrieving issue id suggestions from %s failed: %s", api_url, reason)
            return []
        return self._parse_suggestions(json)  # pragma: no cover behave

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no cover behave
        """Parse the suggestions from the JSON."""
        suggestions = []
        for section in json.get("sections", []):
            for issue in section.get("issues", []):
                suggestions.append(IssueSuggestion(issue["key"], issue["summaryText"]))
        return suggestions

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Return the basic authentication credentials, if any."""
        return (self.username, self.password) if self.username or self.password else None

    def _auth_headers(self) -> dict[str, str]:
        """Return the authorization headers, if any."""
        return dict(Authorization=f"Bearer {self.private_token}") if self.private_token else {}
