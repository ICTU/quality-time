"""Collectors for SonarQube."""

from datetime import datetime, timezone
from typing import Dict

from dateutil.parser import isoparse  # type: ignore
import requests

from ..collector import Collector
from ..type import URL, Units, Value


class SonarQubeViolations(Collector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_parameter = "Subclass responsibility"

    def landing_url(self, **parameters) -> URL:
        url = super().landing_url(**parameters)
        component = parameters.get("component")
        landing_url = f"{url}/project/issues?id={component}&resolved=false"
        return URL(landing_url + self.rules_url_parameter(**parameters))

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
        return URL(api + self.rules_url_parameter(**parameters))

    def rules_url_parameter(self, **parameters) -> str:
        """Return the rules url parameter, if any."""
        rules = parameters.get(self.rules_parameter, [])
        return f"&rules={','.join(rules)}" if rules else ""

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


class SonarQubeComplexUnits(SonarQubeViolations):
    """SonarQube long methods collector."""

    rules_parameter = "complex_unit_rules"


class SonarQubeLongUnits(SonarQubeViolations):
    """SonarQube long methods collector."""

    rules_parameter = "long_unit_rules"


class SonarQubeManyParameters(SonarQubeViolations):
    """SonarQube many parameters methods collector."""

    rules_parameter = "many_parameter_rules"


class SonarQubeMetricsBaseClass(Collector):
    """Base class for collectors that use the SonarQube measures/component API."""

    metricKeys = "Subclass responsibility"

    def landing_url(self, **parameters) -> URL:
        url = super().landing_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/component_measures?id={component}&metric={self.metricKeys}")

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={self.metricKeys}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(self._get_metrics(response)[self.metricKeys])

    @staticmethod
    def _get_metrics(response: requests.Response) -> Dict[str, int]:
        """Get the metric(s) from the response."""
        measures = response.json()["component"]["measures"]
        return dict((measure["metric"], int(measure["value"])) for measure in measures)


class SonarQubeDuplicatedLines(SonarQubeMetricsBaseClass):
    """SonarQube duplicated lines collector."""

    metricKeys = "duplicated_lines"


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


class SonarQubeSourceFreshness(Collector):
    """SonarQube source freshness."""

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/api/project_analyses/search?project={component}")

    def landing_url(self, **parameters) -> URL:
        url = super().landing_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/project/activity?id={component}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str((datetime.now(timezone.utc) - isoparse(response.json()["analyses"][0]["date"])).days)
