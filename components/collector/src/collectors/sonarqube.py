"""Collectors for SonarQube."""

from typing import Dict

import requests

from ..collector import Collector
from ..type import URL, Units, Value


class SonarQubeViolations(Collector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    def landing_url(self, **parameters) -> URL:
        url = super().landing_url(**parameters)
        component = parameters.get("component")
        landing_url = f"{url}/project/issues?id={component}&resolved=false"
        rules = parameters.get("rules")
        if rules:
            landing_url += f"&rules={','.join(rules)}"
        return URL(landing_url)

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
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
        rules = parameters.get("rules")
        if rules:
            api += f"&rules={','.join(rules)}"
        return URL(api)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(response.json()["total"])

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        return [dict(
            key=unit["key"],
            url=self.unit_landing_url(unit["key"], **parameters),
            message=unit["message"],
            severity=unit["severity"].lower(),
            type=unit["type"].lower(),
            component=unit["component"]) for unit in response.json()["issues"]]

    def unit_landing_url(self, unit_key, **parameters):
        """Generate a landing url for the unit."""
        url = super().landing_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/project/issues?id={component}&issues={unit_key}&open={unit_key}")


class SonarQubeLongUnits(SonarQubeViolations):
    """SonarQube long methods collector."""


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


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    metricKeys = "uncovered_lines"


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    metricKeys = "uncovered_conditions"
