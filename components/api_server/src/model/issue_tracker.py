"""Issue tracker."""

import re
from dataclasses import asdict, dataclass, field
from typing import Literal, cast

import requests

from shared.utils.functions import first

from utils.log import get_logger
from utils.type import URL


logger = get_logger()


@dataclass
class AsDictMixin:
    """Mixin class to give data classes an as_dict method."""

    def as_dict(self) -> dict[str, str]:
        """Convert data class to dict."""
        return cast(dict[str, str], asdict(self))  # pragma: no feature-test-cover


@dataclass
class ADFLink(AsDictMixin):
    """Atlassian Document Format link node."""

    attrs: dict[Literal["href"], str]
    type: str = "link"


@dataclass
class ADFText(AsDictMixin):
    """Atlassian Document Format text node."""

    text: str
    marks: list[ADFLink] = field(default_factory=list)
    type: str = "text"


@dataclass
class ADFParagraph(AsDictMixin):
    """Atlassian Document Format paragraph node."""

    content: list[ADFText]
    type: str = "paragraph"


@dataclass
class ADFDocument(AsDictMixin):
    """Atlassian Document Format document node."""

    content: list[ADFParagraph]
    type: str = "doc"
    version: int = 1


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
        return {"Authorization": f"Bearer {self.private_token}"} if self.private_token else {}


@dataclass
class IssueParameters:
    """Parameters to create issues with."""

    project_key: str
    issue_type: str
    issue_labels: list[str] | None = None
    epic_link: str = ""


JiraIssueSuggestionJSON = dict[str, list[dict[str, str | dict[str, str]]]]
JiraIssueTypesJSON = dict[str, list[dict[str, str]]]
JiraFieldsJSON = dict[str, list[dict[str, str]]]
JiraEpicsJSON = dict[str, list[dict[str, str | dict[str, str]]]]
JiraProjectsJSON = list[dict[str, str]]
JiraJSON = JiraEpicsJSON | JiraIssueSuggestionJSON | JiraIssueTypesJSON | JiraFieldsJSON | JiraProjectsJSON


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
    api_version: str
    issue_parameters: IssueParameters
    credentials: IssueTrackerCredentials = field(default_factory=IssueTrackerCredentials)

    def __post_init__(self) -> None:
        """Clean up the parameters.

        - Strip any trailing slash from the URL so we can add paths without worrying about double slashes.
        - Remove the v from the API version.
        """
        self.api_version = self.api_version.lstrip("v")
        self.url = URL(str(self.url).rstrip("/"))

    def create_issue(self, summary: str, description: str = "") -> tuple[str, str]:
        """Create a new issue and return its key or an error message if creating the issue failed."""
        project_key = self.issue_parameters.project_key
        issue_type = self.issue_parameters.issue_type
        labels = self.issue_parameters.issue_labels
        for attribute, name in [(self.url, "URL"), (project_key, "project key"), (issue_type, "issue type")]:
            if not attribute:
                return "", f"Issue tracker has no {name} configured."
        fields: dict[str, str | list[str] | dict[str, str]] = {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
            "description": description if self.api_version == "2" else self.__adf_document(description),
        }
        if labels and self.__labels_supported():  # pragma: no feature-test-cover
            fields["labels"] = self.__prepare_labels(labels)
        epic_link = self.issue_parameters.epic_link
        if epic_link and (epic_link_field_id := self.__epic_link_field_id()):  # pragma: no feature-test-cover
            fields[epic_link_field_id] = epic_link
        try:
            response_json = self.__post_json(self.issue_creation_api, {"fields": fields})
        except Exception as reason:
            error = str(reason) or reason.__class__.__name__
            logger.warning("Creating a new issue at %s failed: %s", self.issue_creation_api, error)
            return "", error
        return response_json["key"], ""  # pragma: no feature-test-cover

    def __adf_document(self, description: str) -> dict:
        """Return the description as Atlassian Document Format (ADF) document."""
        text_nodes = []
        for chunk in re.split(r"[\[\]]", description):  # URLs have the form [anchor|link] in the description
            if "|" in chunk:
                anchor, href = chunk.split("|", maxsplit=1)
                node = ADFText(anchor, marks=[ADFLink({"href": href})])
            else:
                node = ADFText(chunk)
            text_nodes.append(node)
        return ADFDocument([ADFParagraph(text_nodes)]).as_dict()

    def get_options(self) -> Options:
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
        try:
            json = cast(JiraIssueSuggestionJSON, self.__get_json(self.suggestions_api(query)))
        except Exception as reason:
            message = "Retrieving issue id suggestions from %s failed: %s"
            logger.warning(message, self.suggestions_api("<query redacted>"), reason)
            return []
        return self._parse_suggestions(json)  # pragma: no feature-test-cover

    def browse_url(self, issue_key: str) -> URL:
        """Return a URL to a human readable version of the issue."""
        return URL(f"{self.url}/browse/{issue_key}")  # pragma: no feature-test-cover

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
        projects: list[dict] = []
        try:
            projects = cast(JiraProjectsJSON, self.__get_json(self.project_api))
        except Exception as reason:
            logger.warning("Getting issue tracker project options at %s failed: %s", self.project_api, reason)
        return [Option(str(project["key"]), str(project["name"])) for project in projects]

    def __get_issue_type_options(self, projects: list[Option]) -> list[Option]:  # pragma: no feature-test-cover
        """Return the issue tracker issue type options, given the current project."""
        if self.issue_parameters.project_key not in [project.key for project in projects]:
            # Current project is not an option, maybe the credentials were changed? Anyhow, no use getting issue types
            return []
        issue_types = []
        issue_types_json_key = "values" if self.api_version == "2" else "issueTypes"
        try:
            issue_types = cast(JiraIssueTypesJSON, self.__get_json(self.issue_types_api))[issue_types_json_key]
        except Exception as reason:
            logger.warning("Getting issue tracker issue type options at %s failed: %s", self.issue_types_api, reason)
        issue_types = [issue_type for issue_type in issue_types if not issue_type["subtask"]]
        return [Option(str(issue_type["id"]), str(issue_type["name"])) for issue_type in issue_types]

    def __get_field_options(self, issue_types: list[Option]) -> list[Option]:  # pragma: no feature-test-cover
        """Return the issue tracker fields for the current project and issue type."""
        current_issue_type = self.issue_parameters.issue_type
        if current_issue_type not in [issue_type.name for issue_type in issue_types]:
            # Current issue type is not an option, maybe the project was changed? Anyhow, no use getting fields
            return []
        fields = []
        issue_type_id = first(issue_types, lambda issue_type: issue_type.name == current_issue_type).key
        api_url = f"{self.issue_types_api}/{issue_type_id}"
        fields_json_key = "values" if self.api_version == "2" else "fields"
        try:
            fields = cast(JiraFieldsJSON, self.__get_json(api_url))[fields_json_key]
        except Exception as reason:
            logger.warning("Getting issue tracker field options at %s failed: %s", api_url, reason)
        return [Option(str(field["fieldId"]), str(field["name"])) for field in fields]

    def __get_epic_links(self, fields: list[Option]) -> list[Option]:  # pragma: no feature-test-cover
        """Return the possible epic links for the current project."""
        field_names = [field.name.lower() for field in fields]
        if "epic link" not in field_names:
            return []
        epics = []
        try:
            epics = cast(JiraEpicsJSON, self.__get_json(self.epics_api))["issues"]
        except Exception as reason:
            logger.warning("Getting epics at %s failed: %s", self.epics_api, reason)
        return [
            Option(str(epic["key"]), f"{cast(dict[str, dict[str, str]], epic)['fields']['summary']} ({epic['key']})")
            for epic in epics
        ]

    @staticmethod
    def _parse_suggestions(json: JiraIssueSuggestionJSON) -> list[IssueSuggestion]:  # pragma: no feature-test-cover
        """Parse the suggestions from the JSON."""
        issues = json.get("issues", [])
        return [IssueSuggestion(str(issue["key"]), cast(dict, issue["fields"])["summary"]) for issue in issues]

    def __get_json(self, api_url: str) -> JiraJSON:  # pragma: no feature-test-cover
        """Get a response from the API endpoint and return the response JSON."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.get(api_url, auth=auth, headers=headers, timeout=10)
        response.raise_for_status()
        return cast(JiraJSON, response.json())

    def __post_json(self, api_url: str, json) -> dict[str, str]:  # pragma: no feature-test-cover
        """Post the JSON to the API endpoint and return the response JSON."""
        auth, headers = self.credentials.basic_auth_credentials(), self.credentials.auth_headers()
        response = requests.post(api_url, auth=auth, headers=headers, json=json, timeout=10)
        response.raise_for_status()
        return cast(dict[str, str], response.json())

    @property
    def project_api(self) -> str:
        """Return the project endpoint."""
        return f"{self.url}/rest/api/{self.api_version}/project"

    @property
    def issue_creation_api(self) -> str:
        """Return the issue creation endpoint."""
        return f"{self.url}/rest/api/{self.api_version}/issue"

    @property
    def issue_types_api(self) -> str:  # pragma: no feature-test-cover
        """Return the issue types endpoint."""
        return f"{self.issue_creation_api}/createmeta/{self.issue_parameters.project_key}/issuetypes"

    @property
    def epics_api(self) -> str:  # pragma: no feature-test-cover
        """Return the epics endpoint."""
        return (
            f'{self.search_api}?jql=type=epic and ("Epic Status" != Done or "Epic Status" is empty) and '
            f"project={self.issue_parameters.project_key}&fields=summary&maxResults=100"
        )

    def suggestions_api(self, query: str) -> str:
        """Return the suggestions endpoint."""
        # Use proximity search to find at most 20 recent matching issues.
        # See https://confluence.atlassian.com/jirasoftwareserver/search-syntax-for-text-fields-939938747.html.
        return f"{self.search_api}?jql=summary~'{query}~10' order by updated desc&fields=summary&maxResults=20"

    @property
    def search_api(self) -> str:
        """Return the search endpoint."""
        # Assume that if the API version is not v2, we're dealing with Jira Cloud. Change the endpoint accordingly,
        # see https://developer.atlassian.com/changelog/#CHANGE-2046
        endpoint = "search" if self.api_version == "2" else "search/jql"
        return f"{self.url}/rest/api/{self.api_version}/{endpoint}"
