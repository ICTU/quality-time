"""Sources for SonarQube."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, MeasurementResponse, URL


class SonarQubeVersion(Source):
    """SonarQube version source."""

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")


class SonarQubeViolations(Source):
    """SonarQube violations source."""

    def landing_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/project/issues?id={component}&resolved=false")

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/issues/search?componentKeys={component}&resolved=false")

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"])


class SonarQubeMetric(Source):
    """SonarQube component metric source."""

    def landing_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/component_measures?id={component}&metric={metric}")

    def api_url(self, metric: str, url: URL, component: str) -> URL:
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={metric}")

    def parse_source_response(self, metric: str, response: requests.Response) -> Measurement:
        return Measurement(response.json()["component"]["measures"][0]["value"])


class SonarQube(Source):
    """Source class to get measurements from SonarQube."""

    def get(self, metric: str) -> MeasurementResponse:
        delegate = dict(version=SonarQubeVersion, violations=SonarQubeViolations).get(metric, SonarQubeMetric)
        return delegate(self.request).get(metric)
