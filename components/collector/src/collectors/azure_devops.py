"""Azure Devops Server metric collector."""

from typing import List

import requests

from ..collector import Collector
from ..type import Entities, URL, Value


class AzureDevopsBase(Collector):
    """Base class for Azure DevOps collectors."""

    def api_url(self) -> URL:
        url = super().api_url()
        return URL(f"{url}/_apis/wit/wiql?api-version=4.1")

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Override because we need to do a post request and need to separately get the entities."""
        auth = self.basic_auth_credentials()
        response = requests.post(
            api_url, timeout=self.TIMEOUT, auth=auth, json=dict(query=self.parameters.get("wiql", "")))
        ids = ",".join([str(work_item["id"]) for work_item in response.json().get("workItems", [])])
        if not ids:
            return [response]
        work_items_url = URL(f"{super().api_url()}/_apis/wit/workitems?ids={ids}&api-version=4.1")
        return [response, requests.get(work_items_url, timeout=self.TIMEOUT, auth=auth)]

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
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

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(responses[0].json()["workItems"]))


class AzureDevopsReadyUserStoryPoints(AzureDevopsBase):
    """Collector to get ready user story points from Azure Devops Server."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(round(sum(
            [work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints", 0)
             for work_item in responses[1].json()["value"]]))) if len(responses) > 1 else "0"

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        entities = super().parse_source_responses_entities(responses)
        # Add story points to the entities:
        if len(responses) > 1:
            for entity, work_item in zip(entities, responses[1].json()["value"]):
                entity["story_points"] = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
        return entities
