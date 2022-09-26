"""Issue tracker."""

from dataclasses import asdict, dataclass
from typing import cast, Optional
import logging

import requests

from utils.type import URL


class AsDictMixin:  # pylint: disable=too-few-public-methods
    """Mixin class to give data classes a as_dict method."""

    def as_dict(self) -> dict[str, str]:
        """Convert data class to dict."""
        return asdict(self)  # pragma: no cover behave


@dataclass
class IssueSuggestion(AsDictMixin):
    """Issue suggestion."""

    key: str
    text: str


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
class Option(AsDictMixin):
    """Option for an issue tracker attribute."""

    key: str
    name: str


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
        """Strip the URL of trailing slash so we can add paths without worrying about double slashes."""
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
            if labels and self.__labels_supported():  # pragma: no cover behave
                json["fields"]["labels"] = self.__prepare_labels(labels)
            response_json = self.__post_json(api_url, json)
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Creating a new issue at %s failed: %s", api_url, reason)
            return "", str(reason)
        return response_json["key"], ""  # pragma: no cover behave

    def get_options(self) -> dict[str, list[Option]]:  # pragma: no cover behave
        """Return the possible values for the issue tracker attributes."""
        # See https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/#creating-an-issue-examples
        projects = self.__get_project_options()
        issue_types = self.__get_issue_type_options(projects)
        fields = self.__get_field_options(issue_types)
        return dict(projects=projects, issue_types=issue_types, fields=fields)

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

    def __labels_supported(self) -> bool:
        """Return whether the current project and issue type support labels."""
        return "labels" in [field.key for field in self.get_options()["fields"]]

    @staticmethod
    def __prepare_labels(labels: list[str]) -> list[str]:
        """Return the labels in a format accepted by the issue tracker."""
        return [label.replace(" ", "_") for label in labels]  # Jira doesn't allow spaces in labels

    def __get_project_options(self) -> list[Option]:
        """Return the issue tracker projects options, given the current credentials."""
        projects = []
        url = self.project_api % self.url
        try:
            projects = self.__get_json(url)
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Getting issue tracker project options at %s failed: %s", url, reason)
        return [Option(str(project["key"]), str(project["name"])) for project in projects]

    def __get_issue_type_options(self, projects: list[Option]) -> list[Option]:
        """Return the issue tracker issue type options, given the current project."""
        if self.issue_parameters.project_key not in [project.key for project in projects]:
            return []  # Current project is not an option, maybe the credentials were changed, so no issue types as well
        issue_types = []
        url = self.issue_types_api % (self.url, self.issue_parameters.project_key)
        try:
            issue_types = self.__get_json(url)["values"]
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Getting issue tracker issue type options at %s failed: %s", url, reason)
        issue_types = [issue_type for issue_type in issue_types if not issue_type["subtask"]]
        return [Option(str(issue_type["id"]), str(issue_type["name"])) for issue_type in issue_types]

    def __get_field_options(self, issue_types: list[Option]) -> list[Option]:
        """Return the issue tracker fields for the current project and issue type."""
        current_issue_type = self.issue_parameters.issue_type
        if current_issue_type not in [issue_type.name for issue_type in issue_types]:
            return []  # Current issue type is not an option, maybe the project was changed, so no fields as well
        fields = []
        issue_type_id = [issue_type for issue_type in issue_types if issue_type.name == current_issue_type][0].key
        url = f"{self.issue_types_api % (self.url, self.issue_parameters.project_key)}/{issue_type_id}"
        try:
            fields = self.__get_json(url)["values"]
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Getting issue tracker field options at %s failed: %s", url, reason)
        return [Option(str(field["fieldId"]), str(field["name"])) for field in fields]

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no cover behave
        """Parse the suggestions from the JSON."""
        issues = json.get("issues", [])
        return [IssueSuggestion(str(issue["key"]), cast(dict, issue["fields"])["summary"]) for issue in issues]

    def __get_json(self, api_url: str):  # pragma: no cover behave
        """Return the API JSON response."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.get(api_url, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json()

    def __post_json(self, api_url: str, json):  # pragma: no cover behave
        """Post the JSON to the API endpoint and return the response JSON."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.post(api_url, auth=auth, headers=headers, json=json)
        response.raise_for_status()
        return response.json()
