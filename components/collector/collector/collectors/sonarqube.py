"""Collectors for SonarQube."""

from typing import Dict

import requests

from collector.collector import Collector
from collector.type import URL, Units, Value


class SonarQubeViolations(Collector):
    """SonarQube violations collector."""

    def landing_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/project/issues?id={parameters.get('component')}&resolved=false")

    def api_url(self, **parameters) -> URL:
        url = parameters.get("url")
        component = parameters.get("component")
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "units" sent to the server anyway (that limit is 100 currently).
        api = f"{url}/api/issues/search?componentKeys={component}&resolved=false&ps=500"
        severities = ",".join([severity.upper() for severity in parameters.get("severities", [])])
        if severities:
            api += f"&severities={severities}"
        types = ",".join([violation_type.upper() for violation_type in parameters.get("types", [])])
        if types:
            api += f"&types={types}"
        return URL(api)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(response.json()["total"])

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [dict(
            key=unit["key"],
            url=self.unit_landing_url(unit, **parameters),
            message=unit["message"],
            severity=unit["severity"].lower(),
            type=unit["type"].lower(),
            component=unit["component"]) for unit in response.json()["issues"]]

    @staticmethod
    def unit_landing_url(unit, **parameters):
        """Generate a landing url for the unit."""
        return URL(f"{parameters.get('url')}/project/issues?id={parameters.get('component')}&open={unit['key']}")


class SonarQubeMetricsBaseClass(Collector):
    """Base class for collectors that use the SonarQube measures/component API."""

    metricKeys = "Subclass responsibility"

    def landing_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/component_measures"
                   f"?id={parameters.get('component')}&metric={self.metricKeys}")

    def api_url(self, **parameters) -> URL:
        component = parameters.get("component")
        return URL(f"{parameters.get('url')}/api/measures/component?component={component}&metricKeys={self.metricKeys}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(self._get_metrics(response)[self.metricKeys])

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

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        metrics = self._get_metrics(response)
        return str(metrics["lines_to_cover"] - metrics["uncovered_lines"])


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    metricKeys = "uncovered_lines"


class SonarQubeCoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube covered branches."""

    metricKeys = "uncovered_conditions,conditions_to_cover"

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        metrics = self._get_metrics(response)
        return str(metrics["conditions_to_cover"] - metrics["uncovered_conditions"])


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    metricKeys = "uncovered_conditions"
