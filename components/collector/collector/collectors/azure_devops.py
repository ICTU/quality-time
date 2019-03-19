"""Azure Devops Server metric collector."""

import requests

from collector.collector import Collector
from collector.type import Units, URL, Value


class AzureDevopsIssues(Collector):
    """Collector to get issues from Azure Devops Server."""
    request_method = "POST"

    def api_url(self, **parameters) -> URL:
        url = parameters.get("url")
        return URL(f"{url}/_apis/search/workitemsearchresults?api-version=4.1-preview.1")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(response.json()["count"])

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [
            dict(
                key=result["fields"]["system.id"], project=result["project"]["name"],
                title=result["fields"]["system.title"], work_item_type=result["fields"]["system.workitemtype"],
                state=result["fields"]["system.state"], url=result["url"])
            for result in response.json()["results"]]

    @staticmethod
    def json_payload(**parameters):
        payload = {"$top": 100, "filters": {}}
        search_text = parameters.get("search_text")
        if search_text:
            payload["searchText"] = search_text
        for parameter_key, filter_key in (("work_item_types", "WorkItemType"), ("states", "State")):
            parameter_values = parameters.get(parameter_key)
            if parameter_values:
                payload["filters"][f"System.{filter_key}"] = parameter_values
        return payload
