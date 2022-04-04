"""Jira issues collector."""

import itertools
import re

from base_collectors import SourceCollector
from collector_utilities.type import URL, Value
from model import Entities, Entity, SourceMeasurement, SourceResponses


class JiraIssues(SourceCollector):
    """Jira collector for issues."""

    SPRINT_NAME_RE = re.compile(r",name=(.*),startDate=")
    MAX_RESULTS = 500  # Maximum number of issues to retrieve per page. Jira allows at most 500.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field_ids = {}

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Extend to only return the basic auth credentials if no private token is configured.

        This prevents aiohttp from complaining that it "Cannot combine AUTHORIZATION header with AUTH argument or
        credentials encoded in URL"."""
        return None if self._parameter("private_token") else super()._basic_auth_credentials()

    def _headers(self) -> dict[str, str]:  # pylint: disable=no-self-use
        """Extend to add the token, if present, to the headers for the get request."""
        headers = super()._headers()
        if token := self._parameter("private_token"):
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _api_url(self) -> URL:
        """Extend to get the fields from Jira and create a field name to field id mapping."""
        url = await super()._api_url()
        fields_url = URL(f"{url}/rest/api/2/field")
        response = (await super()._get_source_responses(fields_url))[0]
        self._field_ids = {field["name"].lower(): field["id"] for field in await response.json()}
        jql = str(self._parameter("jql", quote=True))
        fields = self._fields()
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields={fields}&maxResults={self.MAX_RESULTS}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the JQL query to the landing URL."""
        url = await super()._landing_url(responses)
        jql = str(self._parameter("jql", quote=True))
        return URL(f"{url}/issues/?jql={jql}")

    def _parameter(self, parameter_key: str, quote: bool = False) -> str | list[str]:
        """Extend to replace field names with field ids, if the parameter is a field."""
        parameter_value = super()._parameter(parameter_key, quote)
        if parameter_key.endswith("field"):
            parameter_value = self._field_ids.get(str(parameter_value).lower(), parameter_value)
        return parameter_value

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Extend to implement pagination."""
        all_responses = SourceResponses(api_url=urls[0])
        for start_at in itertools.count(0, self.MAX_RESULTS):  # pragma: no cover
            responses = await super()._get_source_responses(URL(f"{urls[0]}&startAt={start_at}"), **kwargs)
            if issues := await self._issues(responses):
                all_responses.extend(responses)
            if len(issues) < self.MAX_RESULTS:
                break  # We got fewer than the maximum number of issues per page, so we know we're done
        return all_responses

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to get the issues from the responses."""
        url = URL(str(self._parameter("url")))
        issues = await self._issues(responses)
        entities = Entities(self._create_entity(issue, url) for issue in issues if self._include_issue(issue))
        return SourceMeasurement(value=self._compute_value(entities), entities=entities)

    @staticmethod
    async def _issues(responses: SourceResponses):
        """Return the issues from the responses."""
        issues = []
        for response in responses:
            json = await response.json()
            issues.extend(json.get("issues", []))
        return issues

    @classmethod
    def _compute_value(cls, entities: Entities) -> Value:  # pylint: disable=unused-argument
        """Allow subclasses to compute the value from the entities."""
        return None

    def _create_entity(self, issue: dict, url: URL) -> Entity:  # pylint: disable=no-self-use
        """Create an entity from a Jira issue."""
        # Jira issues have a key and an id. The key consist of the project code and a number, e.g. FOO-42. This means
        # the issue key changes when the issue is moved to another project. The id is an internal key and does not
        # change. Hence, we display the issue key in the UI (issue_key below) but use the id as entity key. This makes
        # sure that when users mark an issue as false positive, it remains false positive even the issue is moved to
        # another project and the issue key changes.
        fields = issue["fields"]
        entity_attributes = dict(
            issue_key=issue["key"],
            created=fields["created"],
            priority=fields.get("priority", {}).get("name"),
            status=fields.get("status", {}).get("name"),
            summary=fields["summary"],
            type=fields.get("issuetype", {}).get("name", "Unknown issue type"),
            updated=fields.get("updated"),
            url=f"{url}/browse/{issue['key']}",
        )
        if sprint_field_id := self._field_ids.get("sprint"):
            entity_attributes["sprint"] = self.__get_sprint_names(fields.get(sprint_field_id) or [])
        return Entity(key=issue["id"], **entity_attributes)

    def _include_issue(self, issue: dict) -> bool:  # pylint: disable=no-self-use,unused-argument
        """Return whether this issue should be counted."""
        return True

    def _fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        sprint_field_id = self._field_ids.get("sprint")
        return "issuetype,summary,created,updated,status,priority" + (f",{sprint_field_id}" if sprint_field_id else "")

    @classmethod
    def __get_sprint_names(cls, sprint_texts: list[str]) -> str:
        """Parse the sprint name from the sprint text."""
        matches = [cls.SPRINT_NAME_RE.search(sprint_text) for sprint_text in sprint_texts]
        sprint_names = [match.group(1) for match in matches if match]
        return ", ".join(sorted(sprint_names))
