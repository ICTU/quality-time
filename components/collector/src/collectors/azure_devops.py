"""Azure Devops Server metric collector."""

from typing import Optional

import requests

from ..collector import Collector
from ..type import Units, URL, Value


class AzureDevopsBase(Collector):
    """Base class for Azure DevOps collectors."""

    def __init__(self) -> None:
        super().__init__()
        self.unit_response: Optional[requests.Response] = None

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        return URL(f"{url}/_apis/wit/wiql?api-version=4.1")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we need to do a post request and need to separately get the units."""
        auth = self.basic_auth_credentials(**parameters)
        response = requests.post(api_url, timeout=self.TIMEOUT, auth=auth, json=dict(query=parameters.get("wiql", "")))
        ids = ",".join([str(work_item["id"]) for work_item in response.json().get("workItems", [])])
        if ids:
            work_items_url = URL(f"{super().api_url(**parameters)}/_apis/wit/workitems?ids={ids}&api-version=4.1")
            self.unit_response = requests.get(work_items_url, timeout=self.TIMEOUT, auth=auth)
        return response

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        if not self.unit_response:
            return []
        return [
            dict(
                key=work_item["id"], project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"], work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"]) for work_item in self.unit_response.json()["value"]]


class AzureDevopsIssues(AzureDevopsBase):
    """Collector to get issues from Azure Devops Server."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(response.json()["workItems"]))


class AzureDevopsReadyUserStoryPoints(AzureDevopsBase):
    """Collector to get ready user story points from Azure Devops Server."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(round(sum(
            [work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints", 0)
             for work_item in self.unit_response.json()["value"]]))) if self.unit_response else "0"

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        units = super().parse_source_response_units(response, **parameters)
        # Add story points to the units:
        if self.unit_response:
            for unit, work_item in zip(units, self.unit_response.json()["value"]):
                unit["story_points"] = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
        return units
