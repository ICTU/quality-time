"""Issue tracker."""

from dataclasses import asdict, dataclass
from typing import cast, Optional
import logging

import requests

from utils.type import URL


class AsDictMixin:  # pylint: disable=too-few-public-methods
    """Mixin class to give data classes an as_dict method."""

    def as_dict(self) -> dict[str, str]:
        """Convert data class to dict."""
        return asdict(self)  # pragma: no feature-test-cover


@dataclass
class IssueSuggestion(AsDictMixin):
    """Issue suggestion."""

    key: str
    text: str


@dataclass(frozen=True)
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
    epic_link: str = ""


JiraIssueSuggestionJSON = dict[str, list[dict[str, str | dict[str, str]]]]


@dataclass
class Option(AsDictMixin):
    """Option for a single choice issue tracker attribute."""

    key: str
    name: str


@dataclass
class Options(AsDictMixin):
    """Options for an issue tracker."""

    projects: list[Option]
    issue_types: list[Option]
    fields: list[Option]
    epic_links: list[Option]


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
    epics_api: str = (
        '%s/rest/api/2/search?jql=type=epic and ("Epic Status" != Done or "Epic Status" is empty) and '
        "project=%s&fields=summary&maxResults=100"
    )

    def __post_init__(self) -> None:
        """Strip any trailing slash from the URL so we can add paths without worrying about double slashes."""
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
        if labels and self.__labels_supported():  # pragma: no feature-test-cover
            json["fields"]["labels"] = self.__prepare_labels(labels)
        epic_link = self.issue_parameters.epic_link
        if epic_link and (epic_link_field_id := self.__epic_link_field_id()):  # pragma: no feature-test-cover
            json["fields"][epic_link_field_id] = epic_link
        try:
            response_json = self.__post_json(api_url, json)
        except Exception as reason:  # pylint: disable=broad-exception-caught
            logging.warning("Creating a new issue at %s failed: %s", api_url, reason)
            return "", str(reason)
        return response_json["key"], ""  # pragma: no feature-test-cover

    def get_options(self) -> Options:  # pragma: no feature-test-cover
        """Return the possible values for the issue tracker attributes."""
        # See https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/#creating-an-issue-examples
        # for more information on how to use the Jira API to discover meta data needed to create issues
        projects = self.__get_project_options()
        issue_types = self.__get_issue_type_options(projects)
        fields = self.__get_field_options(issue_types)
        epic_links = self.__get_epic_links(fields)
        return Options(projects, issue_types, fields, epic_links)

    def get_suggestions(self, query: str) -> list[IssueSuggestion]:
        """Get a list of issue id suggestions based on the query string."""
        api_url = self.suggestions_api % (self.url, query)
        try:
            json = self.__get_json(api_url)
        except Exception as reason:  # pylint: disable=broad-exception-caught
            logging.warning("Retrieving issue id suggestions from %s failed: %s", api_url, reason)
            return []
        return self._parse_suggestions(json)  # pragma: no feature-test-cover

    def browse_url(self, issue_key: str) -> URL:
        """Return a URL to a human readable version of the issue."""
        return URL(self.issue_browse_url % (self.url, issue_key))  # pragma: no feature-test-cover

    def __labels_supported(self) -> bool:  # pragma: no feature-test-cover
        """Return whether the current project and issue type support labels."""
        return "labels" in [field.key for field in self.get_options().fields]

    def __epic_link_field_id(self) -> str:  # pragma: no feature-test-cover
        """Return the id of the epic link field, if any."""
        epic_link_field = [field for field in self.get_options().fields if field.name.lower() == "epic link"]
        return epic_link_field[0].key if epic_link_field else ""

    @staticmethod
    def __prepare_labels(labels: list[str]) -> list[str]:  # pragma: no feature-test-cover
        """Return the labels in a format accepted by the issue tracker."""
        # Jira doesn't allow spaces in labels, so convert them to underscores before creating the issue
        return [label.replace(" ", "_") for label in labels]

    def __get_project_options(self) -> list[Option]:
        """Return the issue tracker projects options, given the current credentials."""
        projects = []
        api_url = self.project_api % self.url
        try:
            projects = self.__get_json(api_url)
        except Exception as reason:  # pylint: disable=broad-exception-caught
            logging.warning("Getting issue tracker project options at %s failed: %s", api_url, reason)
        return [Option(str(project["key"]), str(project["name"])) for project in projects]

    def __get_issue_type_options(self, projects: list[Option]) -> list[Option]:  # pragma: no feature-test-cover
        """Return the issue tracker issue type options, given the current project."""
        if self.issue_parameters.project_key not in [project.key for project in projects]:
            # Current project is not an option, maybe the credentials were changed? Anyhow, no use getting issue types
            return []
        issue_types = []
        api_url = self.issue_types_api % (self.url, self.issue_parameters.project_key)
        try:
            issue_types = self.__get_json(api_url)["values"]
        except Exception as reason:  # pylint: disable=broad-exception-caught
            logging.warning("Getting issue tracker issue type options at %s failed: %s", api_url, reason)
        issue_types = [issue_type for issue_type in issue_types if not issue_type["subtask"]]
        return [Option(str(issue_type["id"]), str(issue_type["name"])) for issue_type in issue_types]

    def __get_field_options(self, issue_types: list[Option]) -> list[Option]:  # pragma: no feature-test-cover
        """Return the issue tracker fields for the current project and issue type."""
        current_issue_type = self.issue_parameters.issue_type
        if current_issue_type not in [issue_type.name for issue_type in issue_types]:
            # Current issue type is not an option, maybe the project was changed? Anyhow, no use getting fields
            return []
        fields = []
        issue_type_id = [issue_type for issue_type in issue_types if issue_type.name == current_issue_type][0].key
        api_url = f"{self.issue_types_api % (self.url, self.issue_parameters.project_key)}/{issue_type_id}"
        try:
            fields = self.__get_json(api_url)["values"]
        except Exception as reason:  # pylint: disable=broad-exception-caught
            logging.warning("Getting issue tracker field options at %s failed: %s", api_url, reason)
        return [Option(str(field["fieldId"]), str(field["name"])) for field in fields]

    def __get_epic_links(self, fields: list[Option]) -> list[Option]:  # pragma: no feature-test-cover
        """Return the possible epic links for the current project."""
        field_names = [field.name.lower() for field in fields]
        if "epic link" not in field_names:
            return []
        api_url = self.epics_api % (self.url, self.issue_parameters.project_key)
        epics = []
        try:
            epics = self.__get_json(api_url)["issues"]
        except Exception as reason:  # pylint: disable=broad-exception-caught
            logging.warning("Getting epics at %s failed: %s", api_url, reason)
        return [Option(str(epic["key"]), str(f'{epic["fields"]["summary"]} ({epic["key"]})')) for epic in epics]

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no feature-test-cover
        """Parse the suggestions from the JSON."""
        issues = json.get("issues", [])
        return [IssueSuggestion(str(issue["key"]), cast(dict, issue["fields"])["summary"]) for issue in issues]

    def __get_json(self, api_url: str):  # pragma: no feature-test-cover
        """Get a response from the API endpoint and return the response JSON."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.get(api_url, auth=auth, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def __post_json(self, api_url: str, json):  # pragma: no feature-test-cover
        """Post the JSON to the API endpoint and return the response JSON."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.post(api_url, auth=auth, headers=headers, json=json, timeout=10)
        response.raise_for_status()
        return response.json()
