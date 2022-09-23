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
class Option:
    """Option for an issue tracker attribute."""

    key: str
    name: str

    def as_dict(self) -> dict[str, str]:
        """Convert option to dict."""
        return asdict(self)  # pragma: no cover behave


@dataclass
class IssueTracker:
    """Issue tracker. Only supports Jira at the moment."""

    url: URL
    issue_parameters: IssueParameters
    credentials: IssueTrackerCredentials = IssueTrackerCredentials()
    project_api = "%s/rest/api/2/project"
    issue_creation_api = "%s/rest/api/2/issue"
    issue_types_api = issue_creation_api + "/createmeta/%s/issuetypes"
    issue_browse_url = "%s/browse/%s"
    suggestions_api: str = "%s/rest/api/2/search?jql=summary~'%s~10' order by updated desc&fields=summary&maxResults=20"

    def __post_init__(self) -> None:
        """Strip the URL of trailing /."""
        self.url = URL(str(self.url).rstrip("/"))

    def create_issue(self, summary: str, description: str = "") -> tuple[str, str]:
        """Create a new issue and return its key or an error message if creating the issue failed."""
        project_key = self.issue_parameters.project_key
        issue_type = self.issue_parameters.issue_type
        labels = self.issue_parameters.issue_labels
        for attribute, name in [(self.url, "URL"), (project_key, "project key"), (issue_type, "issue type")]:
            if not attribute:
                return "", f"Issue tracker has no {name} configured."
        api_url = self.issue_creation_api % self.url
        json = dict(
            fields=dict(
                project=dict(key=project_key), issuetype=dict(name=issue_type), summary=summary, description=description
            )
        )
        try:
            if labels and "labels" in [field.key for field in self.get_options()["fields"]]:
                labels = [label.replace(" ", "_") for label in labels]  # Jira doesn't allow spaces in labels
                json["fields"]["labels"] = labels  # Only add labels if the current project and issue type support them
            response_json = self.__post_json(api_url, json)
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Creating a new issue at %s failed: %s", api_url, reason)
            return "", str(reason)
        return response_json["key"], ""  # pragma: no cover behave

    def get_options(self) -> dict[str, list[Option]]:
        """Return the possible values for the issue tracker attributes."""
        # See https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/#creating-an-issue-examples
        options: dict[str, list[Option]] = dict(projects=[], fields=[], issue_types=[])
        url = project_api_url = self.project_api % self.url
        try:
            projects = self.__get_json(url := project_api_url)
            options["projects"] = [Option(str(project["key"]), str(project["name"])) for project in projects]
            if self.issue_parameters.project_key in [project["key"] for project in projects]:
                issue_types_url = self.issue_types_api % (self.url, self.issue_parameters.project_key)
                all_issue_types = self.__get_json(url := issue_types_url)["values"]
                issue_types = [issue_type for issue_type in all_issue_types if not issue_type["subtask"]]
                options["issue_types"] = [
                    Option(str(issue_type["name"]), str(issue_type["name"])) for issue_type in issue_types
                ]
                if self.issue_parameters.issue_type in [issue_type["name"] for issue_type in issue_types]:
                    issue_type_id = [
                        issue_type
                        for issue_type in issue_types
                        if issue_type["name"] == self.issue_parameters.issue_type
                    ][0]["id"]
                    fields = self.__get_json(url := f"{issue_types_url}/{issue_type_id}")["values"]
                    options["fields"] = [Option(str(field["fieldId"]), str(field["name"])) for field in fields]
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Getting options from creation meta data at %s failed: %s", url, reason)
        return options

    def get_suggestions(self, query: str) -> list[IssueSuggestion]:
        """Get a list of issue id suggestions based on the query string."""
        api_url = self.suggestions_api % (self.url, query)
        try:
            json = self.__get_json(api_url)
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Retrieving issue id suggestions from %s failed: %s", api_url, reason)
            return []
        return self._parse_suggestions(json)  # pragma: no cover behave

    def browse_url(self, issue_key: str) -> URL:
        """Return a URL to a human readable version of the issue."""
        return URL(self.issue_browse_url % (self.url, issue_key))  # pragma: no cover behave

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no cover behave
        """Parse the suggestions from the JSON."""
        issues = json.get("issues", [])
        return [IssueSuggestion(str(issue["key"]), cast(dict, issue["fields"])["summary"]) for issue in issues]

    def __get_json(self, api_url: str):
        """Return the API JSON response."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.get(api_url, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json()

    def __post_json(self, api_url: str, json):
        """Post the JSON to the API endpoint and return the response JSON."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.post(api_url, auth=auth, headers=headers, json=json)
        response.raise_for_status()
        return response.json()
