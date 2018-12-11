"""Sources for SonarQube."""

import requests

from quality_time.source import Source
from quality_time.type import Measurement, URL


class SonarQubeVersion(Source):
    """SonarQube version source."""

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/server/version")


class SonarQubeViolations(Source):
    """SonarQube violations source."""

    def landing_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/project/issues?id={component}&resolved=false")

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/issues/search?componentKeys={component}&resolved=false")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"])


class SonarQubeMetricsBaseClass(Source):
    """Base class for metrics that use the SonarQube measures/component API."""

    metric = "Subclass responsibility"

    def landing_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/component_measures?id={component}&metric={self.metric}")

    def api_url(self, url: URL, component: str) -> URL:
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={self.metric}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["component"]["measures"][0]["value"])


class SonarQubeTests(SonarQubeMetricsBaseClass):
    """SonarQube tests source."""

    metric = "tests"


class SonarQubeFailedTests(SonarQubeMetricsBaseClass):
    """SonarQube failed tests source."""

    metric = "test_failures"


class SonarQubeNCLOC(SonarQubeMetricsBaseClass):
    """SonarQube non-commented lines of code."""

    metric = "ncloc"


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    metric = "lines"
