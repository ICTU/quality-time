"""Jira issues collector."""

import itertools
import re

from collector_utilities.type import URL, Value
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import JiraBase


class JiraIssues(JiraBase):
    """Jira collector for issues."""

    SPRINT_NAME_RE = re.compile(r",name=(.*),startDate=")
    DEFAULT_MAX_RESULTS: int = 500  # Fallback for maximum number of issues to retrieve per page from Jira
    max_results: int | None = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._field_ids: dict[str, str] = {}

    async def _api_url(self) -> URL:
        """Extend to get the fields from Jira and create a field name to field id mapping."""
        url = await super()._api_url()
        fields_url = URL(f"{url}/rest/api/{self._rest_api_version}/field")
        response = (await super()._get_source_responses(fields_url))[0]
        self._field_ids = {}
        for field in await response.json():
            field_name, field_id = field["name"].lower(), field["id"]
            self._field_ids[field_name] = field_id
            self._field_ids[field_id] = field_id  # Include ids too so we get a key error if a field doesn't exist
        jql = str(self._parameter("jql", quote=True))
        fields = self._fields()
        max_results = await self._determine_max_results()
        return URL(f"{url}/rest/api/{self._rest_api_version}/search?jql={jql}&fields={fields}&maxResults={max_results}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the JQL query to the landing URL."""
        url = await super()._landing_url(responses)
        jql = str(self._parameter("jql", quote=True))
        return URL(f"{url}/issues/?jql={jql}")

    def _parameter(self, parameter_key: str, quote: bool = False) -> str | list[str]:
        """Extend to replace field names with field ids, if the parameter is a field."""
        parameter_value = super()._parameter(parameter_key, quote)
        if parameter_value and parameter_key.endswith("field"):
            parameter_value = self._field_ids[str(parameter_value).lower()]
        return parameter_value

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to implement pagination."""
        all_responses = SourceResponses(api_url=urls[0])
        max_results = await self._determine_max_results()
        for start_at in itertools.count(0, max_results):  # pragma: no cover
            responses = await super()._get_source_responses(URL(f"{urls[0]}&startAt={start_at}"))
            if issues := await self._issues(responses):
                all_responses.extend(responses)
            if len(issues) < max_results:
                break  # We got fewer than the maximum number of issues per page, so we know we're done
        return all_responses

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to get the issues from the responses."""
        url = URL(str(self._parameter("url")))
        issues = await self._issues(responses)
        entities = Entities(self._create_entity(issue, url) for issue in issues if self._include_issue(issue))
        return SourceMeasurement(value=self._compute_value(entities), entities=entities)

    @staticmethod
    async def _issues(responses: SourceResponses) -> list[dict]:
        """Return the issues from the responses."""
        issues = []
        for response in responses:
            json = await response.json()
            issues.extend(json.get("issues", []))
        return issues

    @classmethod
    def _compute_value(cls, entities: Entities) -> Value:  # noqa: ARG003
        """Allow subclasses to compute the value from the entities."""
        return None

    def _create_entity(self, issue: dict, url: URL) -> Entity:
        """Create an entity from a Jira issue."""
        # Jira issues have a key and an id. The key consist of the project code and a number, e.g. FOO-42. This means
        # the issue key changes when the issue is moved to another project. The id is an internal key and does not
        # change. Hence, we display the issue key in the UI (issue_key below) but use the id as entity key. This makes
        # sure that when users mark an issue as false positive, it remains false positive even the issue is moved to
        # another project and the issue key changes.
        fields = issue["fields"]
        entity_attributes = {
            "issue_key": issue["key"],
            "created": fields["created"],
            "priority": fields.get("priority", {}).get("name"),
            "status": fields.get("status", {}).get("name"),
            "summary": fields["summary"],
            "type": fields.get("issuetype", {}).get("name", "Unknown issue type"),
            "updated": fields.get("updated"),
            "url": f"{url}/browse/{issue['key']}",
        }
        if sprint_field_id := self._field_ids.get("sprint"):
            entity_attributes["sprint"] = self.__get_sprint_names(fields.get(sprint_field_id) or [])
        return Entity(key=issue["id"], **entity_attributes)

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be counted."""
        return True

    def _fields(self) -> str:
        """Return the fields to get from Jira."""
        sprint_field_id = self._field_ids.get("sprint")
        return "issuetype,summary,created,updated,status,priority" + (f",{sprint_field_id}" if sprint_field_id else "")

    @classmethod
    def __get_sprint_names(cls, sprint_entries: list[str | dict]) -> str:
        """Parse the sprint names from a list of sprint texts or dicts."""
        sprint_names = []
        for sprint_entry in sprint_entries:
            # Difference between Jira cloud and server version, see https://github.com/ICTU/quality-time/issues/11672
            if isinstance(sprint_entry, dict):
                sprint_names.append(sprint_entry["name"])
            elif match := cls.SPRINT_NAME_RE.search(sprint_entry):
                sprint_names.append(match.group(1))
        return ", ".join(sorted(sprint_names))

    async def _determine_max_results(self) -> int:
        """Maximum number of issues to retrieve per page."""
        if isinstance(self.max_results, int):  # NB: using cached_property is not doable on asyncio coroutine
            return self.max_results
        url = self._parameter("url")
        preference_url = URL(f"{url}/rest/api/{self._rest_api_version}/mypreferences?key=jira.search.views.default.max")
        result_value = await (await super()._get_source_responses(preference_url))[0].json()
        self.max_results = result_value if isinstance(result_value, int) else self.DEFAULT_MAX_RESULTS
        return self.max_results
