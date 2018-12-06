from typing import Optional, Sequence

import requests

from quality_time.metric import Metric
from quality_time.metrics import FailedTests, NCLOC, Tests, Version
from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL   


class SonarQube_(Source):
    @classmethod
    def name(cls):
        return "SonarQube"


class SonarQubeVersion(SonarQube_):
    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")

    @classmethod
    def calculate_measurement(cls, source_responses: Sequence[MeasurementResponse]) -> Measurement:
        return Measurement(", ".join([str(source_response["measurement"]) for source_response in source_responses]))


class SonarQubeIssues(SonarQube_):
    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> URL: 
        return URL(f"{url}/project/issues?id={component}&resolved=false")

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/issues/search?componentKeys={component}&resolved=false")

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"] )


class SonarQubeMetric(SonarQube_):
    @classmethod
    def convert_metric_name(cls, metric: Metric) -> str:
        return {FailedTests: "test_failures", Tests: "tests", NCLOC: "ncloc"}[metric]

    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/component_measures?id={component}&metric={metric}")

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={metric}")

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["component"]["measures"][0]["value"])


class SonarQube(Source):
    @classmethod
    def get(cls, metric: Metric, urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        delegate = {Version: SonarQubeVersion}.get(metric, SonarQubeMetric)
        return delegate.get(metric, urls, components)
