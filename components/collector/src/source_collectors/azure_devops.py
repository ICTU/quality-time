"""Azure Devops Server metric collector."""

from abc import ABC
from typing import List

import requests

from utilities.type import Entities, URL, Value
from .source_collector import SourceCollector


class AzureDevopsBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Azure DevOps collectors."""

    MAX_IDS_PER_WORKITEMS_API_CALL = 200  # See
    # https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/work%20items/list?view=azure-devops-rest-5.1

    def _api_url(self) -> URL:
        url = super()._api_url()
        return URL(f"{url}/_apis/wit/wiql?api-version=4.1")

    def _get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Override because we need to do a post request and need to separately get the entities."""
        auth = self._basic_auth_credentials()
        response = requests.post(api_url, timeout=self.TIMEOUT, auth=auth, json=dict(query=self._parameter("wiql")))
        ids = [str(work_item["id"]) for work_item in response.json().get("workItems", [])]
        if not ids:
            return [response]
        ids_string = ",".join(ids[:min(self.MAX_IDS_PER_WORKITEMS_API_CALL, self.MAX_ENTITIES)])
        work_items_url = URL(f"{super()._api_url()}/_apis/wit/workitems?ids={ids_string}&api-version=4.1")
        return [response, requests.get(work_items_url, timeout=self.TIMEOUT, auth=auth)]

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        if len(responses) < 2:
            return []  # We didn't get a response with work items, so assume there are none
        return [
            dict(
                key=str(work_item["id"]), project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"], work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"]) for work_item in responses[1].json()["value"]]


class AzureDevopsIssues(AzureDevopsBase):
    """Collector to get issues from Azure Devops Server."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(responses[0].json()["workItems"]))


class AzureDevopsReadyUserStoryPoints(AzureDevopsBase):
    """Collector to get ready user story points from Azure Devops Server."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(round(sum(
            [work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints", 0)
             for work_item in responses[1].json()["value"]]))) if len(responses) > 1 else "0"

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        entities = super()._parse_source_responses_entities(responses)
        # Add story points to the entities:
        if len(responses) > 1:
            for entity, work_item in zip(entities, responses[1].json()["value"]):
                entity["story_points"] = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
        return entities
