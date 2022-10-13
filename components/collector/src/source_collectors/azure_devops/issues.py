"""Azure DevOps Server issues collector."""

from itertools import chain
from typing import Final

import aiohttp

from base_collectors import SourceCollector
from collector_utilities.functions import iterable_to_batches
from collector_utilities.type import URL, Value, Responses
from model import Entities, Entity, SourceMeasurement, SourceResponses


class AzureDevopsIssues(SourceCollector):
    """Collector to get issues from Azure Devops Server."""

    MAX_IDS_PER_WORK_ITEMS_API_CALL: Final[int] = 200  # See
    # https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/work%20items/list?view=azure-devops-rest-5.1

    async def _api_url(self) -> URL:
        """Extend to add the WIQL or WorkItems API path."""
        return URL(f"{await super()._api_url()}/_apis/wit/wiql?api-version=6.0")

    def _api_list_query(self) -> dict[str, str]:
        """Combine API select and where fields to correct WIQL query."""
        wiql_query_segments = [f"Select [System.Id] From WorkItems"]
        wiql_parameter = self._parameter("wiql")
        if wiql_parameter:
            if not wiql_parameter.startswith("WHERE"):
                wiql_query_segments.append("WHERE")
            wiql_query_segments.append(wiql_parameter)
        return dict(query=" ".join(wiql_query_segments))

    def _item_select_fields(self) -> list[str]:
        """Return the API fields to select for individual issues."""
        return ["System.TeamProject", "System.Title", "System.WorkItemType", "System.State"]

    async def _get_work_items(self, auth: aiohttp.BasicAuth, ids: list[int]) -> Responses:
        """Separately get each work item from the API."""
        api_url = (await self._api_url()).replace('wit/wiql', 'wit/workitemsbatch')
        id_iter = iterable_to_batches(ids, min(self.MAX_IDS_PER_WORK_ITEMS_API_CALL, SourceMeasurement.MAX_ENTITIES))
        responses = [
            await self._session.post(api_url, auth=auth, json=dict(ids=id_batch, fields=self._item_select_fields()))
            for id_batch in id_iter
        ]
        return responses

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Override because we need to do a post request and need to separately get the entities."""
        api_url = urls[0]
        auth = aiohttp.BasicAuth(str(self._parameter("private_token")))
        response = await self._session.post(api_url, auth=auth, json=self._api_list_query())
        ids = [work_item["id"] for work_item in (await response.json()).get("workItems", [])]
        if not ids:
            return SourceResponses(responses=[response], api_url=api_url)
        work_items = await self._get_work_items(auth, ids)
        work_items.insert(0, response)
        return SourceResponses(responses=work_items, api_url=api_url)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the work items from the WIQL query response."""
        return Entities(
            Entity(
                key=work_item["id"],
                project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"],
                work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"],
            )
            for work_item in await self._work_items(responses)
        )

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the value from the responses.

        We can't just count the entities because due to pagination the response may not contain all work items.
        """
        return str(len((await responses[0].json())["workItems"]))

    def _include_issue(self, issue: dict) -> bool:  # pylint: disable=unused-argument # skipcq: PYL-R0201
        """Return whether this issue should be counted."""
        return True

    async def _work_items(self, responses: SourceResponses) -> list[dict]:
        """Return the work items, if any."""
        if len(responses) <= 1:  # the first call is to workItems, which only returns ids
            return []

        all_work_items = chain.from_iterable([(await response.json()).get("value") for response in responses[1:]])
        return [work_item for work_item in all_work_items if self._include_issue(work_item)]
