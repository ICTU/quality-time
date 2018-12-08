"""Sources for SonarQube."""

from typing import Sequence

import requests

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class SonarQubeVersion(Source):
    """SonarQube version source."""

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")


class SonarQubeIssues(Source):
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


class SonarQubeMetric(Source):
    """SonarQube component metric source."""

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

    @classmethod
    def get(cls, metric: str, urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        delegate = dict(version=SonarQubeVersion, violations=SonarQubeIssues).get(metric, SonarQubeMetric)
        return delegate.get(metric, urls, components)
