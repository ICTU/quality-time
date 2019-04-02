"""Gitlab metric source."""

from typing import Optional, Tuple
from urllib.parse import quote

import requests

from ..collector import Collector
from ..type import URL, Value


class GitlabFailedJobs(Collector):
    """Collector class to get failed job counts from Gitlab."""

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        project = quote(str(parameters.get("project")), safe="")
        api_url = f"{url}/api/v4/projects/{project}/jobs"
        private_token = parameters.get("private_token")
        if private_token:
            api_url += f"?private_token={private_token}"
        return URL(api_url)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len([job for job in response.json() if job["status"] == "failed"]))

    @staticmethod
    def basic_auth_credentials(**parameters) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as URI parameter
