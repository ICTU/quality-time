"""Sources for SonarQube."""

from typing import Sequence, Type

import requests

from quality_time.metric import Metric
from quality_time.metrics import FailedTests, NCLOC, Tests, Version
from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class _SonarQube(Source):
    """Base class for metric-specific SonarQube sources."""

    @classmethod
    def name(cls):
        return "SonarQube"


class SonarQubeVersion(_SonarQube):
    """SonarQube version source."""

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")


class SonarQubeIssues(_SonarQube):
    """SonarQube issue source."""

    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/project/issues?id={component}&resolved=false")

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/issues/search?componentKeys={component}&resolved=false")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"])


class SonarQubeMetric(_SonarQube):
    """SonarQube component metric source."""

    @classmethod
    def convert_metric_name(cls, metric: Type[Metric]) -> str:
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
    """Source class to get measurements from SonarQube."""

    API = "sonarqube"

    @classmethod
    def get(cls, metric: Type[Metric], urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        delegate = SonarQubeVersion if metric == Version else SonarQubeMetric
        return delegate.get(metric, urls, components)
