"""Azure Devops Server issues collector."""

from typing import Final

import aiohttp

from base_collectors import SourceCollector
from collector_utilities.type import URL, Value
from model import Entities, Entity, SourceMeasurement, SourceResponses


class AzureDevopsIssues(SourceCollector):
    """Collector to get issues from Azure Devops Server."""

    MAX_IDS_PER_WORK_ITEMS_API_CALL: Final[int] = 200  # See
    # https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/work%20items/list?view=azure-devops-rest-5.1

    async def _api_url(self) -> URL:
        """Extend to add the WIQL API path."""
        return URL(f"{await super()._api_url()}/_apis/wit/wiql?api-version=4.1")

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Override because we need to do a post request and need to separately get the entities."""
        api_url = urls[0]
        auth = aiohttp.BasicAuth(str(self._parameter("private_token")))
        response = await self._session.post(api_url, auth=auth, json=dict(query=self._parameter("wiql")))
        ids = [str(work_item["id"]) for work_item in (await response.json()).get("workItems", [])]
        if not ids:
            return SourceResponses(responses=[response], api_url=api_url)
        ids_string = ",".join(ids[: min(self.MAX_IDS_PER_WORK_ITEMS_API_CALL, SourceMeasurement.MAX_ENTITIES)])
        work_items_url = URL(f"{await super()._api_url()}/_apis/wit/workitems?ids={ids_string}&api-version=4.1")
        work_items = await super()._get_source_responses(work_items_url, **kwargs)
        work_items.insert(0, response)
        return work_items

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

    @staticmethod
    async def _work_items(responses: SourceResponses):
        """Return the work items, if any."""
        return (await responses[1].json())["value"] if len(responses) > 1 else []
