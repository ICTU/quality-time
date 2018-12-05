from typing import Optional

import requests

from .source import Source
from .types import Measurement, MeasurementResponse, URL   


class SonarQube_(Source):
    @classmethod
    def name(cls):
        return "SonarQube"


class SonarQubeVersion(SonarQube_):
    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.text)


class SonarQubeIssues(SonarQube_):
    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> Optional[URL]:
        return URL(f"{url}/project/issues?id={component}&resolved=false")

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/issues/search?componentKeys={component}&resolved=false")

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"] )


class SonarQubeMetric(SonarQube_):
    @classmethod
    def convert_metric_name(cls, metric: str) -> str:
        return "test_failures" if metric == "failed_tests" else metric

    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> Optional[URL]:
        return URL(f"{url}/component_measures?id={component}&metric={metric}")

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={metric}")

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["component"]["measures"][0]["value"])


class SonarQube(Source):
    @classmethod
    def get(cls, metric: str, url: URL, component: str = None) -> MeasurementResponse:
        delegate = dict(version=SonarQubeVersion, issues=SonarQubeIssues).get(metric, SonarQubeMetric)
        return delegate.get(metric, url, component)
