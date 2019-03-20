"""Azure Devops Server metric collector."""

import requests

from collector.collector import Collector
from collector.type import Units, URL, Value


class AzureDevopsIssues(Collector):
    """Collector to get issues from Azure Devops Server."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_response = None

    def api_url(self, **parameters) -> URL:
        url = parameters.get("url")
        return URL(f"{url}/_apis/wit/wiql?api-version=4.1")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we need to do a post request and need to separately get the units."""
        auth = self.basic_auth_credentials(**parameters)
        response = requests.post(api_url, timeout=self.TIMEOUT, auth=auth, json=dict(query=parameters.get("wiql", "")))
        ids = ",".join([str(work_item["id"]) for work_item in response.json().get("workItems", [])[:self.MAX_UNITS]])
        if ids:
            work_items_url = URL(f"{parameters.get('url')}/_apis/wit/workitems?ids={ids}&api-version=4.1")
            self.unit_response = requests.get(work_items_url, timeout=self.TIMEOUT, auth=auth)
        return response

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(response.json()["workItems"]))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        if not self.unit_response:
            return []
        return [
            dict(
                key=result["id"], project=result["fields"]["System.TeamProject"],
                title=result["fields"]["System.Title"], work_item_type=result["fields"]["System.WorkItemType"],
                state=result["fields"]["System.State"],
                url=result["url"]) for result in self.unit_response.json()["value"]]
