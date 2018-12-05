import requests

from .source import Source
from .types import Measurement, URL


class Jenkins(Source):
    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/json?tree=jobs[buildable,color]")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        if metric == "failing_jobs":
            jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))
