"""Collectors for SonarQube."""

from typing import Dict, List

from dateutil.parser import isoparse  # type: ignore
import requests

from ..collector import Collector
from ..type import URL, Entities, Entity, Parameter, Value
from ..util import days_ago


class SonarQubeViolations(Collector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_parameter = "Subclass responsibility"

    def landing_url(self, responses: List[requests.Response], **parameters: Parameter) -> URL:
        url = super().landing_url(responses, **parameters)
        component = parameters.get("component")
        landing_url = f"{url}/project/issues?id={component}&resolved=false"
        return URL(landing_url + self.rules_url_parameter(**parameters))

    def api_url(self, **parameters: Parameter) -> URL:
        url = super().api_url(**parameters)
        component = parameters.get("component")
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 100 currently).
        api = f"{url}/api/issues/search?componentKeys={component}&resolved=false&ps=500"
        severities = ",".join([severity.upper() for severity in parameters.get("severities", [])])
        if severities:
            api += f"&severities={severities}"
        types = ",".join([violation_type.upper() for violation_type in parameters.get("types", [])])
        if types:
            api += f"&types={types}"
        return URL(api + self.rules_url_parameter(**parameters))

    def rules_url_parameter(self, **parameters: Parameter) -> str:
        """Return the rules url parameter, if any."""
        rules = parameters.get(self.rules_parameter, [])
        return f"&rules={','.join(rules)}" if rules else ""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        return str(sum(int(response.json()["total"]) for response in responses))

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters: Parameter) -> Entities:
        return [self.entity(issue, response, **parameters)
                for response in responses for issue in response.json()["issues"]]

    def issue_landing_url(self, issue_key: str, response: requests.Response, **parameters: Parameter) -> URL:
        """Generate a landing url for the issue."""
        url = super().landing_url([response], **parameters)
        component = parameters.get("component")
        return URL(f"{url}/project/issues?id={component}&issues={issue_key}&open={issue_key}")

    def entity(self, issue, response: requests.Response, **parameters: Parameter) -> Entity:
        """Create an entity from an issue."""
        return dict(
            key=issue["key"],
            url=self.issue_landing_url(issue["key"], response, **parameters),
            message=issue["message"],
            severity=issue["severity"].lower(),
            type=issue["type"].lower(),
            component=issue["component"])


class SonarQubeCommentedOutCode(SonarQubeViolations):
    """SonarQube commented out code collector."""

    rules_parameter = "commented_out_rules"


class SonarQubeComplexUnits(SonarQubeViolations):
    """SonarQube long methods collector."""

    rules_parameter = "complex_unit_rules"


class SonarQubeLongUnits(SonarQubeViolations):
    """SonarQube long methods collector."""

    rules_parameter = "long_unit_rules"


class SonarQubeManyParameters(SonarQubeViolations):
    """SonarQube many parameters collector."""

    rules_parameter = "many_parameter_rules"


class SonarQubeSuppressedViolations(SonarQubeViolations):
    """SonarQube suppressed violations collector."""

    rules_parameter = "suppression_rules"

    def get_source_responses(self, api_url: URL, **parameters: Parameter) -> List[requests.Response]:
        """Next to the suppressed rules, also get issues closed as false positive and won't fix from SonarQube."""
        responses = super().get_source_responses(api_url, **parameters)
        url = Collector.api_url(self, **parameters)
        component = parameters.get("component")
        api_url = URL(f"{url}/api/issues/search?componentKeys={component}&status=RESOLVED&"
                      "resolutions=WONTFIX,FALSE-POSITIVE&ps=500")
        return responses + [requests.get(api_url, timeout=self.TIMEOUT, auth=self.basic_auth_credentials(**parameters))]

    def entity(self, issue, response: requests.Response, **parameters: Parameter) -> Entity:
        """Also add the resolution to the entity."""
        entity = super().entity(issue, response, **parameters)
        resolution = issue.get("resolution", "").lower()
        entity["resolution"] = dict(wontfix="won't fix").get(resolution, resolution)
        return entity


class SonarQubeMetricsBaseClass(Collector):
    """Base class for collectors that use the SonarQube measures/component API."""

    metricKeys = "Subclass responsibility"

    def landing_url(self, responses: List[requests.Response], **parameters: Parameter) -> URL:
        url = super().landing_url(responses, **parameters)
        component = parameters.get("component")
        return URL(f"{url}/component_measures?id={component}&metric={self.metricKeys}")

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={self.metricKeys}")

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        return str(self._get_metrics(responses)[self.metricKeys])

    @staticmethod
    def _get_metrics(responses: List[requests.Response]) -> Dict[str, int]:
        """Get the metric(s) from the responses."""
        measures = [measure for measure in responses[0].json()["component"]["measures"]]
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


class SonarQubeSourceUpToDateness(Collector):
    """SonarQube source up-to-dateness."""

    def api_url(self, **parameters: Parameter) -> URL:
        url = super().api_url(**parameters)
        component = parameters.get("component")
        return URL(f"{url}/api/project_analyses/search?project={component}")

    def landing_url(self, responses: List[requests.Response], **parameters: Parameter) -> URL:
        url = super().landing_url(responses, **parameters)
        component = parameters.get("component")
        return URL(f"{url}/project/activity?id={component}")

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        analysis_datetime = isoparse(responses[0].json()["analyses"][0]["date"])
        return str(days_ago(analysis_datetime))
