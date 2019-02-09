"""Collectors for SonarQube."""

from typing import Dict

import requests

from collector.collector import Collector
from collector.type import Measurement, Units, URL


class SonarQubeVersion(Collector):
    """SonarQube version collectior."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/server/version")


class SonarQubeViolations(Collector):
    """SonarQube violations collector."""

    def landing_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/project/issues?id={parameters.get('component')}&resolved=false")

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/api/issues/search"
                   f"?componentKeys={parameters.get('component')}&resolved=false")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["total"])

    def parse_source_response_units(self, source, response: requests.Response) -> Units:  # pylint: disable=no-self-use
        """Parse the response to get the units for the metric."""
        def unit_landing_url(unit, **parameters):
            """Generate a landing url for the unit."""
            return URL(f"{parameters.get('url')}/project/issues?id={parameters.get('component')}&open={unit['key']}")

        return [dict(key=unit["key"], url=unit_landing_url(unit, **source.get("parameters", {})),
                     message=unit["message"], component=unit["component"]) for unit in response.json()["issues"]]


class SonarQubeMetricsBaseClass(Collector):
    """Base class for collectors that use the SonarQube measures/component API."""

    metricKeys = "Subclass responsibility"

    def landing_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/component_measures"
                   f"?id={parameters.get('component')}&metric={self.metricKeys}")

    def api_url(self, **parameters) -> URL:
        component = parameters.get("component")
        return URL(f"{parameters.get('url')}/api/measures/component?component={component}&metricKeys={self.metricKeys}")

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(self._get_metrics(response)[self.metricKeys])

    @staticmethod
    def _get_metrics(response: requests.Response) -> Dict[str, int]:
        """Get the metric(s) from the response."""
        measures = response.json()["component"]["measures"]
        return dict((measure["metric"], int(measure["value"])) for measure in measures)


class SonarQubeTests(SonarQubeMetricsBaseClass):
    """SonarQube tests collector."""

    metricKeys = "tests"


class SonarQubeFailedTests(SonarQubeMetricsBaseClass):
    """SonarQube failed tests collector."""

    metricKeys = "test_failures"


class SonarQubeNCLOC(SonarQubeMetricsBaseClass):
    """SonarQube non-commented lines of code."""

    metricKeys = "ncloc"


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    metricKeys = "lines"


class SonarQubeCoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube covered lines of code."""

    metricKeys = "uncovered_lines,lines_to_cover"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        metrics = self._get_metrics(response)
        return Measurement(metrics["lines_to_cover"] - metrics["uncovered_lines"])


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    metricKeys = "uncovered_lines"


class SonarQubeCoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube covered branches."""

    metricKeys = "uncovered_conditions,conditions_to_cover"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        metrics = self._get_metrics(response)
        return Measurement(metrics["conditions_to_cover"] - metrics["uncovered_conditions"])


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    metricKeys = "uncovered_conditions"
