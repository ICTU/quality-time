"""Issue tracker."""

from dataclasses import dataclass
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
        return dict(key=self.key, text=self.text)


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
            json = response.json()
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Retrieving issue id suggestions from %s failed: %s", api_url, reason)
            return []
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
