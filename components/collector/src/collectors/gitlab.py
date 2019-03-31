"""Gitlab metric source."""

from typing import Optional, Tuple

import requests

from ..collector import Collector
from ..type import URL, Value


class GitlabFailedJobs(Collector):
    """Collector class to get failed job counts from Gitlab."""

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        return URL(f"{url}/api/v4/projects/{parameters.get('project')}/"
                   f"jobs?private_token={parameters.get('private_token')}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len([job for job in response.json() if job["status"] == "failed"]))

    @staticmethod
    def basic_auth_credentials(**parameters) -> Optional[Tuple[str, str]]:
        return None  # The private token is passed as URI parameter
