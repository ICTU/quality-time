"""Jenkins metric source."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, URL


class Jenkins(Source):
    """Source class to get measurements from Jenkins."""

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/json?tree=jobs[buildable,color]")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        if metric == "failed_jobs":
            jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))
